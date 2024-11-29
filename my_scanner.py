from tokens import TOKENS, INSTRUCTIONS
import argparse

class Token:
    def __init__(self, type_, value):
        self.type = type_	# type of token, eg. TOK_IDENTIFIER, TOK_TRAIT...
        self.value = value	# value of token

# https://docs.python.org/3/library/functions.html#repr
    def __repr__(self):
        return f'<({self.type}, {self.value})>'
    
class Scanner:
    def __init__(self, file_path):
        try:
            with open(file_path, 'r') as file:
                self.input = file.read()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            self.input = ''
        except IOError:
            print(f"Error: Could not read file '{file_path}'.")
            self.input = ''
        self.cur_index = 0
        self.tokens = []
        # Error reporting
        self.errors = []
        self.line = 1
        self.column = 1
    
    def get_next_char(self):
        if self.cur_index >= len(self.input):
            return None		# this should be the end of the input
        char = self.input[self.cur_index]
        self.cur_index += 1

        if char == '\n':
            self.line += 1
            self.column = 1 # reset column at new line
        else:
            self.column += 1

        return char
    
    def get_position(self):
        return self.line, self.column
    
    def peek_char(self):
        # peak at the next char without incrementing
        if self.cur_index >= len(self.input):
            return None
        return self.input[self.cur_index]
    
    def add_token(self, token_type, value=None):
        if value is None:
            value = TOKENS.get(token_type, token_type)
        token = Token(token_type, value)
        self.tokens.append(token)

    # tokenize a boolean value
    def scan_boolean(self):
        next_word = ''
        while self.peek_char() and self.peek_char().isalpha():
            next_word += self.get_next_char()
        
        if next_word == TOKENS['TOK_YES'] or next_word.lower() == 'true':
            return True
        elif next_word == TOKENS['TOK_NO'] or next_word.lower() == 'false':
            return False
        else:
            # Signal an invalid boolean
            self.add_token('TOK_ERROR', f"Invalid boolean value: {next_word}")
            return None

    # tokenize a NUMBER and its value
    def scan_number(self, first_digit):
        no = first_digit
        while self.peek_char() and self.peek_char().isdigit():
            no += self.get_next_char()
        if no.isdigit():
            self.add_token('TOK_NUMBER', int(no))
        else:
            self.add_token('TOK_ERROR', None)

    def scan_instruction(self, first_word):
        instruction_parts = [first_word]

        # in case the instruction is a single word
        instruction = ' '.join(instruction_parts)
        if instruction in INSTRUCTIONS:
            return instruction, INSTRUCTIONS[instruction]
    
        # else, instruction may be multiple words
        while self.peek_char() == ' ':
            self.get_next_char() # ignore the space
            next_word = ''
            while self.peek_char() and self.peek_char().isalnum():
                next_word += self.get_next_char()
        
            instruction_parts.append(next_word)
            instruction = ' '.join(instruction_parts)

            if instruction in INSTRUCTIONS:
                return instruction, INSTRUCTIONS[instruction]
        
        # not an instruction
        return None, None

    # main scanning function
    def scan(self):
        while self.cur_index < len(self.input):
            char = self.get_next_char()

            if char.isspace():
                continue	# ignore spaces, newlines

            elif char.isalpha():
                self.scan_word(char)

            elif char.isdigit():
                self.scan_number(char)
            
            elif char == '=':
                self.add_token('TOK_EQUALS')
            elif char == ',':
                self.add_token('TOK_COMMA')
            else: # unexpected character (not isalpha or isdigit) 

                # ignore and try to continue, log error messages
                line, column = self.get_position()
                # self.errors.append(f"Error: Unexpected character '{char}' at line {line}, column {column}")    defunct
                self.add_token('TOK_ERROR', f"Error: Unexepcted character '{char}' at line {line}, column {column}")
                continue

        return self.tokens

    def scan_word(self, first_char):
        word = first_char
        # maximum munches till the next space
        while self.peek_char() and self.peek_char().isalnum():
            word += self.get_next_char()
        
        if word.endswith(','):
            word=word.rstrip(',')
        if not word:
            return # skip empty value due to extra comma 

        # first checks for instructions
        instruction, token = self.scan_instruction(word)
        if token:
            self.add_token(token, instruction)
            return

        if word == TOKENS['TOK_CHARACTERS']:
            self.add_token('TOK_CHARACTERS')

        elif word == TOKENS['TOK_TRAIT']:
            self.add_token('TOK_TRAIT')

        elif word == TOKENS['TOK_EVIL']:
            self.add_token('TOK_EVIL')

        elif word == TOKENS['TOK_STRENGTH']:
            self.add_token('TOK_STRENGTH')

        elif word == TOKENS['TOK_SCENES']:
            self.add_token('TOK_SCENES')

        # TODO: for 'event', we must include everything until some marking character 
        elif word == TOKENS['TOK_EVENT']:
            self.add_token('TOK_EVENT')
            
            event_desc = ""

            if self.peek_char() == '=':
                self.get_next_char()
                self.add_token('TOK_EQUALS')

            # Skip spaces
            while self.peek_char() and self.peek_char().isspace():
                self.get_next_char()

            # include everything until the next newline or line break
            while self.peek_char() and self.peek_char() not in ['\n', '\r']:
                event_desc += self.get_next_char()

            self.add_token('TOK_IDENTIFIER', event_desc.strip())

        elif word == TOKENS['TOK_LOCATION']:
            self.add_token('TOK_LOCATION')

        elif word == TOKENS['TOK_YES'] or word.lower() == 'true':
            self.add_token('TOK_YES', True)
        elif word == TOKENS['TOK_NO'] or word.lower() == 'false':
            self.add_token('TOK_NO', False)
        else:
            # must be IDENTIFIER (variable name or string 'value'), catch all case
            self.add_token('TOK_IDENTIFIER', word)

def main():
    parser = argparse.ArgumentParser(description = 'Scanner Program')
    parser.add_argument('file', help = 'Please enter the path to the input file')
    args = parser.parse_args()

    # print(f"Processing file: {args.file}")

    scanner = Scanner(args.file)
    tokens = scanner.scan()
    
    for token in tokens:
        print(token)
    
    # For error reporting during tokenization,
    # not currently being used
    if scanner.errors: 
        print("\nErrors: ")
        for error in scanner.errors:
            print(error)

if __name__ == '__main__':
    main()
