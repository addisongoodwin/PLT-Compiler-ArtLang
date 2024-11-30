from tokens import TOKENS, INSTRUCTIONS
import argparse
import json
import re

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  # List of tokens from the scanner
        self.token_index = 0  # Track the current token index
        self.ast = []  # Output: Abstract Syntax Tree (AST)
        self.errors = []  # Error stream for error messages
        
        self.current_token = self.tokens[0] if tokens else None

    '''
    TODO:
    Upon encountering a fatal TOK_ERROR, try to skip forward to the next recognizable block
    and continue parsing. Even if the parser fails in the end, the parser will output a complete
    list of errors. 
    '''
    def recover(self):
        print(f"In recovery function.....")

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None # end of token input

    def match(self, expected_token):
        if self.current_token and self.current_token[0] == expected_token:
            self.advance()
            return True
        else:
            self.errors.append(f"Syntax error: Expected type '{expected_token} but found
                               type '{self.current_token[0]}")
            return False
    
    ''' Main parsing function '''
    def parse(self):
        while self.current_token:
            try:
                block = self.parse_token()
                if block:
                    self.ast.append(block)
            except Exception as e:
                self.errors.append(f"Error: {str(e)}")
                self.recover()
            
        return self.ast # final return
    
    def parse_block(self):
        token = self.current_token
        if token == "TOK_CHARACTERS":
            return parse_character_block()
        elif token == "TOK_SCENES":
            return parse_scene_block()
        elif token in INSTRUCTIONS:
            return parse_instruction_block()
        elif token == "TOK_ERROR":
            # TODO: probably have to recover
            # self.handle_error(token)
            print(f"Error: TOK_ERROR encountered in parse_block()")
            self.advance() # just skip for now
        else:
            # TODO: Some strange token means Scanner probably messed up
            self.errors.append(f"Unexpected token: '{token}'")
            self.advance() # try to ignore it anyways??? or crash????????????????

        return None
    
    """
    Restricted assignments are for values that must be of certain types:
        TOK_EVIL: boolean value
        TOK_STRENGTH: integer value
    """
    def parse_restricted_assignment(self, token_type):
        self.match(token_type)
        if self.match("TOK_EQUALS"): # basically just consume the TOK_EQUALS
            if token_type == "TOK_EVIL":
                value = self.current_token and self.current_token[0] == "TOK_YES"
                self.advance()
                return {"type": "restricted_assignment", "evil": value}
        
            elif token_type == "TOK_STRENGTH":
                value = int(self.current_token[1]) if self.current_token and self.current_token[0] == "TOK_NUMBER" else 0
                self.advance()
                return {"type": "restricted_assignment", "strength": value}




# TODO: Handle TOK_ERROR tokens fatal to the parser
def handle_error(token):
    if token == "TOK_ERROR":
        if token is None:
            print("Syntax Error: Unexpected token. Expected a valid token, but found None.")
        else:
            print(f"Syntax Error: Unexpected token value '{token}'.")
    print(f"Syntax Error: Unexpected token value '{token}'.")
    # raise ValueError("Parsing stopped due to unknown token.")



def parse_program(tokens):
    return {"type": "program", "block": parse_block_list(tokens)}

def parse_block_list(tokens):
    blocks = []
    while tokens:
        block = parse_block(tokens)
        if block:
            blocks.append(block)
        else:
            break
    return blocks

# Character block
def parse_character_definition(tokens):
    definition = []
    # Stop if we encounter tokens that signal the end of a character or character block
    while tokens and tokens[0][0] not in ["TOK_SCENES", "TOK_WRITE_STORY_INST", "TOK_PRINT_CHARACTER_INST", "TOK_IDENTIFIER"]:
        detail = parse_character_detail(tokens)
        if detail:
            definition.append(detail)
    return definition

def parse_character_block(tokens):
    tokens.pop(0)  # Remove TOK_CHARACTERS
    characters = []

    # Parse each character block a non-character token
    while tokens and tokens[0][0] == "TOK_IDENTIFIER":
        character_name = tokens.pop(0)[1]  # Get character name
        character_definition = parse_character_definition(tokens)
        characters.append({
            "type": "character_block",
            "name": character_name,
            "definition": character_definition
        })
    
    # check that we're not stuck on an error token
    if tokens and tokens[0][0] == "TOK_ERROR":
        handle_error(tokens.pop(0))

    return characters

def parse_character_detail(tokens):
    if tokens[0][0] == "TOK_EVIL":
        return parse_restricted_assignment(tokens)
    elif tokens[0][0] == "TOK_TRAIT":
        return parse_trait_list(tokens)
    elif tokens[0][0] == "TOK_STRENGTH":
        return parse_restricted_assignment(tokens)
    elif tokens[0][0] in ["TOK_EQUALS", "TOK_COMMA", "TOK_ERROR"]:
        print(f"Stuck on '{tokens[0][0]}', discarding...")
        tokens.pop(0)  # Discard the token
        handle_error(tokens[0][0]) # fail, maybe
    return None

def parse_restricted_assignment(tokens):
    if not tokens:
        handle_error(("TOK_ERROR", "Expected TOK_EVIL or TOK_STRENGTH"))
        return
    
    token_type, token_value = tokens.pop(0)
    
    if token_type == "TOK_EVIL":
        # Expect an '=' token; assign False by default if no valid value follows
        if tokens and tokens[0][0] == "TOK_EQUALS":
            tokens.pop(0)  # Remove TOK_EQUALS
            if tokens and tokens[0][0] in ["TOK_YES", "TOK_NO"]:
                # Consume the boolean token and set evil accordingly
                return {"type": "restricted_assignment", "evil": tokens.pop(0)[0] == "TOK_YES"}
            else:
                # Default to False if no valid boolean value follows
                return {"type": "restricted_assignment", "evil": False}

    elif token_type == "TOK_STRENGTH":
        # Expect an '=' token; assign 0 by default if no valid number follows
        if tokens and tokens[0][0] == "TOK_EQUALS":
            tokens.pop(0)  # Remove TOK_EQUALS
            if tokens and tokens[0][0] == "TOK_NUMBER":
                # Consume the number token and set strength
                strength = int(tokens.pop(0)[1])
            else:
                # Default to 0 if no valid number follows
                strength = 0

        return {"type": "restricted_assignment", "strength": strength}


# def parse_boolean(tokens):
#     bool_value = tokens.pop(0)[0]
#     return bool_value == 

def parse_trait_list(tokens):
    tokens.pop(0)  # Remove TOK_TRAIT
    tokens.pop(0)  # Remove TOK_EQUALS
    return {"type": "trait_list", "traits": parse_trait_assignment_t(tokens)}

def parse_trait_assignment_t(tokens):
    traits = []
    while tokens and tokens[0][0] in ["TOK_IDENTIFIER", "TOK_COMMA"]:
        if tokens[0][0] == "TOK_IDENTIFIER":
            traits.append(tokens.pop(0)[1])
        elif tokens[0][0] == "TOK_COMMA":
            tokens.pop(0)  # Skip comma
    return traits
# end Character block

# Scene block
def parse_scene_block(tokens):
    tokens.pop(0)  # Remove TOK_SCENES
    scenes = []
    while tokens and tokens[0][0] == "TOK_IDENTIFIER":
        scenes.append(parse_new_scene(tokens))
    # check that we're not stuck on an error token
    if tokens[0][0] == "TOK_ERROR":
        handle_error(tokens[0][0])
    return scenes

def parse_new_scene(tokens):
    scene_name = tokens.pop(0)[1]  # Scene name
    return {
        "type": "scene_block",
        "name": scene_name,
        "details": parse_scene_definition(tokens)
    }

def parse_scene_definition(tokens):
    details = []
    while tokens and tokens[0][0] not in ["TOK_CHARACTERS", "TOK_SCENES", "TOK_WRITE_STORY_INST", "TOK_PRINT_CHARACTER_INST"]:
        detail = parse_scene_detail(tokens)
        if detail:
            details.append(detail)
        else:
            break
    return details

def parse_scene_detail(tokens):
    if tokens[0][0] == "TOK_LOCATION":
        return parse_location_assignment(tokens)
    elif tokens[0][0] == "TOK_IDENTIFIER" and tokens[0][1] == "characters":
        return parse_characters_present(tokens)
    elif tokens[0][0] == "TOK_EVENT":
        return parse_event_assignment(tokens)
    return None

def parse_location_assignment(tokens):
    tokens.pop(0)  # Remove TOK_LOCATION
    tokens.pop(0)  # Remove TOK_EQUALS
    location_name = tokens.pop(0)[1]
    return {"type": "location_assignment", "location": location_name}

def parse_event_assignment(tokens):
    tokens.pop(0)  # Remove TOK_EVENT
    tokens.pop(0)  # Remove TOK_EQUALS
    event_description = tokens.pop(0)[1]
    return {"type": "event_assignment", "event": event_description}

def parse_characters_present(tokens):
    tokens.pop(0)  # Remove TOK_IDENTIFIER (characters)
    tokens.pop(0)  # Remove TOK_EQUALS
    return {"type": "characters_present", "characters": parse_character_list(tokens)}

def parse_character_list(tokens):
    characters = []
    while tokens and tokens[0][0] != "TOK_EVENT" and tokens[0][0] != "TOK_SCENES":
        if tokens[0][0] == "TOK_IDENTIFIER":
            characters.append(tokens.pop(0)[1])
        elif tokens[0][0] == "TOK_COMMA":
            tokens.pop(0)  # Skip comma
    return characters

# end Scene block

def parse_instruction_block(tokens):
    inst_type, inst_value = tokens.pop(0)
    instruction_block = {
        "type": "instruction_block",
        "instruction": inst_type
    }
    if inst_type == "TOK_PRINT_CHARACTER_INST":
        if tokens and tokens[0][0] == "TOK_IDENTIFIER":
            _, character_name = tokens.pop(0)
            instruction_block["character_name"] = character_name
        else:
            instruction_block["character_name"] = None  # Ok, we will print all the characters
    elif inst_type == "TOK_WRITE_STORY_INST":
        instruction_block["content"] = "write the story"
    return instruction_block

# Process the input file by removing extra characters in token, probably unnecessary 
def read_input(file_path):
    tokens = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(r'<\((\w+),\s*(.*?)\)>', line.strip()) # thanks to chatGPT for this line :o 
            if match:
                token_type, token_value = match.groups()
                tokens.append((token_type, token_value))
    return tokens

def main():
    parser = argparse.ArgumentParser(description = 'Parser Program')
    parser.add_argument('file', help = 'Please enter the path to the input file')
    args = parser.parse_args()

    # print(f"Processing file: {args.file}")

    tokens = read_input(args.file)
    my_parser = Parser(tokens)
          
    ast = parse_program(tokens)
    
    if (my_parser.errors):
        for error in my_parser.errors:
            print(f"{error}")
    
    print(json.dumps(ast, indent=4))

# if __name__ == '__main__':
# 	main()
