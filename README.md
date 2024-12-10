# PLT Programming Assignment Compiler -- ArtLang
Addison Goodwin, ag4423

## Context-free Grammar & Production Rules

```
program 			-> statement_list
statement_list 			-> statement statement_list | ε

statement			-> character_block | scene_block | instruction

character_block			-> TOK_CHARACTERS TOK_IDENTIFIER character_definition
scene_block			-> TOK_SCENES new_scene |  ε
instruction			-> TOK_WRITE_STORY_INST | TOK_PRINT_CHARACTER_INST

character_definition		-> character_detail | character_definition |  ε
character_detail		-> restricted_assignment | trait_list
restricted_assignment 		-> TOK_EVIL boolean | TOK_STRENGTH TOK_EQUALS TOK_NUMBER

trait_list			-> TOK_TRAIT TOK_EQUALS trait_assignment_t
trait_assignment_t		-> TOK_IDENTIFIER | TOK_COMMA TOK_IDENTIFIER trait_assignment_t | ε

new_scene	 		-> TOK_IDENTIFIER scene_definition
scene_definition		-> scene_detail scene_definition | ε
scene_detail			-> location_assignment | characters_present | event_assignment

location_assignment		-> TOK_LOCATION TOK_EQUALS TOK_IDENTIFIER
event_assignment		-> TOK_EVENT TOK_EQUALS TOK_IDENTIFIER
characters_present		-> TOK_IDENTIFIER TOK_EQUALS character_list
character_list			-> TOK_IDENTIFIER character_list_t | ε
character_list_t		-> TOK_COMMA TOK_IDENTIFIER character_list_t | ε

boolean				-> TOK_TRUE | TOK_FALSE
```

```
		NON-TERMINALS				TERMINALS
----------------------------			----------------------------
program						TOK_CHARACTERS
statement					TOK_IDENTIFIER
statement_list					TOK_SCENES
character_block					TOK_WRITE_STORY_INST
scene_block					TOK_PRINT_CHARACTER_INST
instruction					TOK_EVIL
character_definition				TOK_STRENGTH
new_scene					TOK_TRAIT
trait_list					TOK_LOCATION
boolean						TOK_EVENT
trait_assignment_t				TOK_COMMA
scene_detail					TOK_EQUALS
scene_definition				TOK_NUMBER
location_assignment
characters_present
event_assignment
character_list
character_list_t
```

## Change List
### ArtLang.py
- The main pipline workflow for the compiler.
- Runs scanner.py --> parser.py --> code_generator.py sequentially.
- Currently, each step saves its output (`tokens.txt`, `AST.json`, and the final story `story.txt`) into the user-specified folder for my error checking.
- Captures and displays errors for each step and prints them to terminal as to not pollute the output, and input to the next phase in the compiler.
- Errors will not stop subsequent steps, ensuring all outputs are attempted.

To run ArtLang.py:
Requires Python 3.12.0 for best compatability (see below for instructions for running with Docker)
```
python ArtLang.py <input_program.txt> --output_folder <output_dir_name>
```
  
### Scanner
Error tracking:
- Separated token output and error output, so that user-facing errors are not sent to the parser.
- Added line and column tracking for unrecognized characters and other errors.

Other:
- Expanded accepted boolean values to include `true` and `false`. Now `yes, no, true, false` are acceptable.

Changes to processing of`TOK_EQUALS` token:
- Removed tight coupling of `TOK_EVIL` with `TOK_EQUALS` to produce a `<TOK_EVIL, value>` token. This was difficult to handle in the parser, because there are other occurrences of `TOK_EQUALS` not so tightly coupled.
- same change made for `<TOK_STRENGTH, value>`. 
- Going forward:
	- The input `evil = yes` will be parsed as `<TOK_EVIL>`, `TOK_EQUALS`,`<TOK_BOOLEAN, TRUE>`. 
	- The input `strength = 10` will be parsed as `<TOK_STRENGTH>`, `<TOK_EQUALS>`,  `<TOK_NUMBER, 10>`, and we will ensure robust correctness during parsing.
 ### Parser
 - Now utilizes a `class Parser` for consistency with the design in Scanner, and to allow for better management of parsing logic and error reporting. I find writing this way greatly improves code-readability.

- Added the `advance(self)` function that increments a counter and moves to the next token.
- Added the `match(self, expected type)` function to check if the current token matches the expected token. If so, returns true and calls `advance()`, else it will add a generic error message about incorrect tokens to the error stream.
- Added the `recover(self)` function: Upon encountering a fatal TOK_ERROR, try to skip forward to the next recognizable block and continue parsing. Even if the parser fails in the end, the parser will output a complete list of errors.
#### Error handling in the parser
- Added explicit defaults for the following cases, when assignment is absent:
	Characters block:
		- Strength defaults to 0.
		- Evil defaults to false.

- If the assignment is malformed rather than missing, we will stop and return errors, because that seems to indicate the user wanted some specific assignment or otherwise doesn't understand the language well enough to be successful.

- Right now, the parser prints scary "ERROR: " statements, but most of the time these do not cause the parser to fail, and it is able to put out a clean AST. It ignores and disregards invalid characters, used in assignment or otherwise, and will try to handle weird tokens too. The output could be improved to indicate that it was not a fatal error, and just warn the user that they are writing unrecognized characters.


## How to Build and Run

### 1. Clone the Repository

After cloning the repository, navigate to the project directory.

### 2. Build the Docker Image

Use the provided Dockerfile to build the Docker image:
Note that you must be in the project directory to use the `.` directory, otherwise please specify the directory.
```
docker build -t parser-image .
```

### Run the Docker Container
```
docker run parser-image
```  

## Understanding Output of parser.py

The shell script should run automatically and display results of all 5 tests to the terminal as well as a file `full_test_output.txt` for covenient viewing with the logs section of the Docker container, terminal, or from the resulting `.txt` file.

The output of lexer.py is used as input for parser.py. The inputs files can be found in the `/lexer_input` directory, and the corresponding output (and input to the parser) can be found in `/lexer_output`.

### Error Handling
I moved much of the error handing I was doing during lexical analysis into the parsing. I felt that some of the corrections were syntatic errors, and thus should be handled in the parser. I want to try to implement automatic error fixing, for example assigning default values of `'0'` for when an invalid value is passed into the `strength` property, but it is not quite implemented yet. It is sucessfully catching errors and trying to continue forwards for the most part, only stopping when it gets really confused or "misalligned" during the recursive descent parsing.
