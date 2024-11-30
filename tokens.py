SHARED_TOKENS = {
    'TOK_IDENTIFIER': 'IDENTIFIER', 		# general variable name
    'TOK_ERROR': 'error'
}

CHARACTER_TOKENS = {
    'TOK_CHARACTERS': 'Characters',
    'TOK_TRAIT': 'trait',
    'TOK_EVIL': 'evil',
    'TOK_STRENGTH': 'strength',
    **SHARED_TOKENS
}

SCENE_TOKENS = {
    'TOK_SCENES': 'Scenes',
    'TOK_EVENT': 'event',
    'TOK_LOCATION': 'location',
    **SHARED_TOKENS
}

OTHER_TOKENS = {
    'TOK_YES': 'yes',						# boolean: 1, true
    'TOK_NO': 'no',							# boolean: 0, false
    'TOK_NUMBER': 'NUMBER', 				# ints for strength
    'TOK_EQUALS': '=',
    'TOK_COMMA': ',',
    **SHARED_TOKENS
}

INSTRUCTIONS = {
    'write story': 'TOK_WRITE_STORY_INST',  
    'print character': 'TOK_PRINT_CHARACTER_INST',
    **SHARED_TOKENS
}
# only works with python 3.9 or newer
TOKENS = CHARACTER_TOKENS | SCENE_TOKENS | OTHER_TOKENS | INSTRUCTIONS