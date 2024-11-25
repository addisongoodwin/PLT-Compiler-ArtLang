# PLT Programming Assignment 2 - Parser
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

## lexer.py Patch Notes
1. Corrected a typo so that `TOK_CHARACTERS` is correctly tokenized.
Previously the token was `TOK_CHARACTER`, but this failed to correctly tokenize into the `TOK_CHARACTERS` token meant to specify the start of the character definition block.

2. Removed print statements used for clarity during Part 1 submission but that are not suitable as input into the parser.

3. Removed tokenization of the `=` tokenized as `TOK_EQUALS` during tokenization of the value in `TOK_EVIL`. The value of `TOK_EQUALS` is captured into the token during lexical analysis, so this `=` is only annoying during parsing.

4. Added `TOK_ERROR` token to the lexer such that the parser might be able to identify errors and sugguest or autofix mistakes, depending on where it is in the tree. The lexer now tokenizes `TOK_ERROR` and the error value rather than printing an error message.

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
