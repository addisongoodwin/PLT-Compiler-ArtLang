# PLT Programming Assignment Compiler -- ArtLang
Addison Goodwin, ag4423

## How to Run ArtLang.py:

### Using Docker

#### 1. Clone the Repository

After cloning the repository, navigate to the project directory.

#### 2. Build the Docker Image

Use the provided Dockerfile to build the Docker image:
Note that you must be in the project directory to use the `.` directory, otherwise please specify the directory.
```
docker build -t plt_compiler .
```

#### Run the Docker Container
The provided shell script will run automatically.
```
docker run --name plt_compiler_tests plt_compiler
```

#### Access Results (Optional)
ArtLang.py outputs results to files in folders. You can mount a volume to view them on your host, if you'd like. I've provided them as well in the repo.
Replace `output` with the actual directories where results are stored (see run_ArtLang.sh to see the directories)
```
docker run -v $(pwd)/output:/app/output --name plt_compiler_tests plt_compiler
```

### Manually
Requires Python 3.12.0 for best compatability (see below for instructions for running with Docker)

```
python ArtLang.py <input_program.txt> --output_folder <output_dir_name>
```

## Understanding Output

### Test 1: easy and simple program that tests the`print characters` instructions to list select characters
###### Test 2: invalid characters
- invalid characters are tokenized as `TOK_ERR`, then reported as errors during parsing.
- Most invalid characters are discarded without much problem, the parser builds and AST and the compiler ends with successful story generation.
- Shows succesful recognition of bad characters in the scanner, and shows robustness in the parser.
###### Test 3: long input
- A more challenging example. Runs twice, once to demonstrate the `write story` instruction, and again to demonstrate the `print characters` instruction.
- Long to show that the tokenizer, parser, and story generation are robust enough to handle long (albeit clean) inputs.
###### Test 4: example of failure
- Just fails due to unfixable syntax errors and missing values in the sample program, but prints some good error information to indicate where the issue is.
###### Test 5: weird values
- long lists of traits, weird (negative) or long values for strength, and very long event descriptions.
- Works as expected for both story generation and character listing.

## Change List
### ArtLang.py
- The main pipline workflow for the compiler.
- Runs scanner.py --> parser.py --> code_generator.py sequentially.
- Currently, each step saves its output (`tokens.txt`, `AST.json`, and the final story `story.txt`) into the user-specified folder for my error checking.
- Captures and displays errors for each step and prints them to terminal as to not pollute the output, and input to the next phase in the compiler.
- Errors will not stop subsequent steps, ensuring all outputs are attempted.
- 
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

## Demo Video
https://youtu.be/nWeYXcnL9fk

Thanks very much to the TAs and Professor for all your hard work this semester, I struggled a lot but learned a lot :)
