import argparse
import json
import re
from tokens import (
    TOK_IDENTIFIER, TOK_ERROR, TOK_EQUALS, TOK_COMMA,
    TOK_CHARACTERS, TOK_TRAIT, TOK_EVIL, TOK_STRENGTH,
    TOK_SCENES, TOK_EVENT, TOK_LOCATION,
    TOK_YES, TOK_NO, TOK_NUMBER,
    TOK_WRITE_STORY_INST, TOK_PRINT_CHARACTER_INST, TOKENS, INSTRUCTIONS
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = 0
        self.ast = []
        self.errors = []
        self.current_token = self.tokens[0] if tokens else None

    def advance(self):
        """Move to the next token."""
        self.token_index += 1
        self.current_token = self.tokens[self.token_index] if self.token_index < len(self.tokens) else None

    def match(self, expected_token):
        """Match the expected token or record an error."""
        if self.current_token and self.current_token[0] == expected_token:
            self.advance()
            return True
        self.errors.append(f"Expected {expected_token} but found {self.current_token}")
        return False
    
    def peek_next_token_type(self):
        next_index = self.token_index + 1
        if next_index < len(self.tokens):
            return self.tokens[next_index][0]
        return None

    def recover(self):
        """Skip tokens until a synchronization token is found."""
        sync_tokens = {TOK_CHARACTERS, TOK_SCENES, TOK_WRITE_STORY_INST, TOK_PRINT_CHARACTER_INST}
        while self.current_token and self.current_token[0] not in sync_tokens:
            print(f"Skipping: {self.current_token}")
            self.advance()

    def parse(self):
        """Start parsing the input and construct the AST."""
        while self.current_token:
            try:
                block = self.parse_block()
                if block:
                    self.ast.append(block)
            except Exception as e:
                self.errors.append(str(e))
                self.recover()
        return self.ast

    def parse_block(self):
        """Parse top-level blocks."""
        if self.current_token[0] == TOK_CHARACTERS:
            return self.parse_character_block()
        elif self.current_token[0] == TOK_SCENES:
            return self.parse_scene_block()
        elif self.current_token[0] in {TOK_WRITE_STORY_INST, TOK_PRINT_CHARACTER_INST}:
            return self.parse_instruction_block()
        elif self.current_token[0] == TOK_ERROR:
            self.errors.append(f"Encountered TOK_ERROR: {self.current_token}")
            self.advance()
        else:
            self.errors.append(f"Unexpected token: {self.current_token}")
            self.recover()
        return None

# character block
    def parse_character_block(self):
        """Parse a character block."""
        self.match(TOK_CHARACTERS)
        characters = []

        while self.current_token:
            if self.current_token[0] in {TOK_SCENES, TOK_WRITE_STORY_INST, TOK_PRINT_CHARACTER_INST}:
                # Stop processing when we encounter a scene block or instruction
                break
            elif self.current_token[0] == TOK_IDENTIFIER:  # Character name
                name = self.current_token[1]
                self.advance()
                definition = self.parse_character_definition()
                characters.append({
                    "type": "character_block",
                    "name": name,
                    "definition": definition
                })
            else:
                # Skip unexpected tokens
                self.errors.append(f"Unexpected token in character block: {self.current_token}")
                self.advance()

        return characters

    def parse_character_definition(self):
        """Parse character details like evil, strength, and traits."""
        definition = []

        while self.current_token:
            if self.current_token[0] in {TOK_SCENES, TOK_WRITE_STORY_INST, TOK_PRINT_CHARACTER_INST, TOK_IDENTIFIER}:
                # Stop when encountering scene blocks, instructions, or a new character
                break
            elif self.current_token[0] == TOK_EVIL:
                definition.append(self.parse_restricted_assignment(TOK_EVIL))
            elif self.current_token[0] == TOK_STRENGTH:
                definition.append(self.parse_restricted_assignment(TOK_STRENGTH))
            elif self.current_token[0] == TOK_TRAIT:
                definition.append(self.parse_trait_list())
            elif self.current_token[0] in {TOK_EQUALS, TOK_COMMA}:
                # Skip stray tokens
                print(f"Skipping unexpected token: {self.current_token}")
                self.advance()
            else:
                # Handle unexpected tokens gracefully
                self.errors.append(f"Unexpected token in character detail: {self.current_token}")
                self.advance()

        return definition

    def parse_character_detail(self):
        """Parse specific character details."""
        if self.current_token[0] == TOK_EVIL:
            return self.parse_restricted_assignment(TOK_EVIL)
        elif self.current_token[0] == TOK_STRENGTH:
            return self.parse_restricted_assignment(TOK_STRENGTH)
        elif self.current_token[0] == TOK_TRAIT:
            return self.parse_trait_list()
        elif self.current_token[0] in {TOK_EQUALS, TOK_COMMA}:
            print(f"Skipping unexpected token: {self.current_token}")
            self.advance()
        else:
            self.errors.append(f"Unexpected token in character detail: {self.current_token}")
            self.advance()
        return None

    def parse_restricted_assignment(self, token_type):
        """Parse assignments like TOK_EVIL and TOK_STRENGTH with error handling."""
        self.match(token_type)
        if not self.match(TOK_EQUALS):  # If '=' is missing, skip this assignment
            self.errors.append(f"Missing '=' after {token_type}")
            return None

        if token_type == TOK_EVIL:
            # Handle missing or invalid values for 'evil'
            if self.current_token and self.current_token[0] in {TOK_YES, TOK_NO}:
                value = self.current_token[0] == TOK_YES  # Convert TOK_YES/TOK_NO to boolean
                self.advance()
                return {"type": "restricted_assignment", "evil": value}
            else:
                self.errors.append(f"Missing or invalid value for 'evil' after '=', assigned default 'False'")
                return {"type": "restricted_assignment", "evil": False}  # Default value

        elif token_type == TOK_STRENGTH:
            # Handle missing or invalid values for 'strength'
            if self.current_token and self.current_token[0] == TOK_NUMBER:
                value = int(self.current_token[1])
                self.advance()
                return {"type": "restricted_assignment", "strength": value}
            else:
                self.errors.append(f"Missing or invalid value for 'strength' after '=', assigned default '0'")
                return {"type": "restricted_assignment", "strength": 0}  # Default value

    def parse_trait_list(self):
        """Parse a list of traits."""
        self.match(TOK_TRAIT)
        self.match(TOK_EQUALS)
        traits = []
        while self.current_token and self.current_token[0] in {TOK_IDENTIFIER, TOK_COMMA}:
            if self.current_token[0] == TOK_IDENTIFIER:
                traits.append(self.current_token[1])
            self.advance()
        return {"type": "trait_list", "traits": traits}
# end character block
    
# scene block
    def parse_scene_block(self):
        """Parse a scene block."""
        self.match(TOK_SCENES)  # Match the 'Scenes' token
        scenes = []

        while self.current_token:
            if self.current_token[0] in {TOK_CHARACTERS, TOK_WRITE_STORY_INST, TOK_PRINT_CHARACTER_INST}:
                # Stop parsing when encountering a new block
                break
            elif self.current_token[0] == TOK_IDENTIFIER:  # Scene name
                scene_name = self.current_token[1]
                self.advance()
                scene_details = self.parse_scene_definition()
                scenes.append({
                    "type": "scene_block",
                    "name": scene_name,
                    "details": scene_details
                })
            else:
                # Skip unexpected tokens
                self.errors.append(f"Unexpected token in scene block: {self.current_token}")
                self.advance()

        return {"type": "scene_block_list", "scenes": scenes}

# TODO ???
    def parse_new_scene(self):
        """Parse a single scene."""
        scene_name = self.current_token[1]
        self.advance()
        return {"type": "scene_block", "name": scene_name, "details": self.parse_scene_definition()}

    def parse_scene_definition(self):
        """Parse details within a scene."""
        details = []

        while self.current_token:
            # Stop if encountering a new scene, characters block, or instructions
            if self.current_token[0] in {TOK_SCENES, TOK_CHARACTERS, TOK_WRITE_STORY_INST, TOK_PRINT_CHARACTER_INST}:
                break
            # Stop if encountering a new scene name (TOK_IDENTIFIER)
            elif self.current_token[0] == TOK_IDENTIFIER and self.peek_next_token_type() != TOK_EQUALS:
                break
            elif self.current_token[0] == TOK_LOCATION:
                details.append(self.parse_location_assignment())
            elif self.current_token[0] == TOK_EVENT:
                details.append(self.parse_event_assignment())
            elif self.current_token[0] == TOK_IDENTIFIER and self.current_token[1] == "characters":
                details.append(self.parse_characters_present())
            else:
                # Skip unexpected tokens
                self.errors.append(f"Unexpected token in scene definition: {self.current_token}")
                self.advance()

        return details

    def parse_location_assignment(self):
        """Parse a location assignment."""
        self.match(TOK_LOCATION)
        self.match(TOK_EQUALS)
        location = self.current_token[1]
        self.advance()
        return {"type": "location_assignment", "location": location}

    def parse_event_assignment(self):
        """Parse an event assignment."""
        self.match(TOK_EVENT)
        self.match(TOK_EQUALS)
        event = self.current_token[1]
        self.advance()
        return {"type": "event_assignment", "event": event}
    
    def parse_characters_present(self):
        """Parse the list of characters present in a scene."""
        self.match(TOK_IDENTIFIER)  # Match 'characters'
        self.match(TOK_EQUALS)
        characters = []

        while self.current_token and self.current_token[0] in {TOK_IDENTIFIER, TOK_COMMA}:
            if self.current_token[0] == TOK_IDENTIFIER:
                characters.append(self.current_token[1])
            self.advance()

        return {"type": "characters_present", "characters": characters}
# end scene block

    def parse_instruction_block(self):
        """Parse instructions like 'write story' or 'print character'."""
        inst_type = self.current_token[0]
        self.advance()
        if inst_type == TOK_PRINT_CHARACTER_INST:
            return {"type": "instruction_block", "instruction": inst_type}
        elif inst_type == TOK_WRITE_STORY_INST:
            return {"type": "instruction_block", "content": "write story"}


def read_input(file_path):
    """Read input file and tokenize it."""
    tokens = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(r'<\((\w+),\s*(.*?)\)>', line.strip())
            if match:
                token_type, token_value = match.groups()
                tokens.append((token_type, token_value))
    return tokens


def main():
    parser = argparse.ArgumentParser(description="Parser")
    parser.add_argument("file", help="Path to the input file")
    args = parser.parse_args()

    tokens = read_input(args.file)
    my_parser = Parser(tokens)
    ast = my_parser.parse()

    if my_parser.errors:
        for error in my_parser.errors:
            print(f"Error: {error}")
    else:
        print("Parsing complete successfully.")
    print(json.dumps(ast, indent=4))


if __name__ == "__main__":
    main()