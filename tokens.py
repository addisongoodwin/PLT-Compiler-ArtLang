# Shared tokens
TOK_IDENTIFIER = 'TOK_IDENTIFIER'
TOK_ERROR = 'TOK_ERROR'
TOK_EQUALS = 'TOK_EQUALS'
TOK_COMMA = 'TOK_COMMA'

# Character tokens
TOK_CHARACTERS = 'TOK_CHARACTERS'
TOK_TRAIT = 'TOK_TRAIT'
TOK_EVIL = 'TOK_EVIL'
TOK_STRENGTH = 'TOK_STRENGTH'

# Scene tokens
TOK_SCENES = 'TOK_SCENES'
TOK_EVENT = 'TOK_EVENT'
TOK_LOCATION = 'TOK_LOCATION'

# Other tokens
TOK_YES = 'TOK_YES'
TOK_NO = 'TOK_NO'
TOK_NUMBER = 'TOK_NUMBER'

# Instructions
TOK_WRITE_STORY_INST = 'TOK_WRITE_STORY_INST'
TOK_PRINT_CHARACTER_INST = 'TOK_PRINT_CHARACTER_INST'

INSTRUCTIONS = {
    "write story": "TOK_WRITE_STORY_INST",
    "print character": "TOK_PRINT_CHARACTER_INST"
}

# Unified TOKENS dictionary for validation (optional)
TOKENS = {
    TOK_IDENTIFIER: 'IDENTIFIER',
    TOK_ERROR: 'error',
    TOK_EQUALS: '=',
    TOK_COMMA: ',',
    TOK_CHARACTERS: 'Characters',
    TOK_TRAIT: 'trait',
    TOK_EVIL: 'evil',
    TOK_STRENGTH: 'strength',
    TOK_SCENES: 'Scenes',
    TOK_EVENT: 'event',
    TOK_LOCATION: 'location',
    TOK_YES: 'yes',
    TOK_NO: 'no',
    TOK_NUMBER: 'NUMBER',
    TOK_WRITE_STORY_INST: 'write story',
    TOK_PRINT_CHARACTER_INST: 'print character'
}