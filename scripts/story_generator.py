import argparse
import json

def load_ast(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def process_characters(character_blocks):
    characters = {}
    for block in character_blocks:
        name = block["name"]
        traits = []
        evil = False
        strength = 0  # Default to 0 if not specified

        for detail in block["definition"]:
            if detail["type"] == "trait_list":
                traits.extend(detail["traits"])
            elif detail["type"] == "restricted_assignment":
                if "evil" in detail:
                    evil = detail["evil"]
                if "strength" in detail:
                    strength = detail["strength"]

        characters[name] = {"traits": traits, "evil": evil, "strength": strength}
    return characters

def print_characters_instruction(characters, specified_characters=None):
    lines = []

    # Determine characters to print: all or specified ones
    if not specified_characters:
        specified_characters = characters.keys()

    for name in specified_characters:
        if name in characters:
            char = characters[name]
            traits = ", ".join(char["traits"])
            evil = "yes" if char["evil"] else "no"
            strength = char["strength"]
            lines.append(f"{name} -> Traits: {traits}, Evil: {evil}, Strength: {strength}")
        else:
            lines.append(f"{name} -> Character not found.")

    return "\n".join(lines)

def generate_story(ast):
    character_blocks, scenes, instruction = ast[0], ast[1]["scenes"], ast[2]
    characters = process_characters(character_blocks)

    story_lines = []

    # Process each scene
    for scene in scenes:
        location = None
        event = None
        present_characters = []

        for detail in scene["details"]:
            if detail["type"] == "location_assignment":
                location = detail["location"]
            elif detail["type"] == "characters_present":
                present_characters = detail["characters"]
            elif detail["type"] == "event_assignment":
                event = detail["event"]

        # Generate scene narrative
        if location:
            story_lines.append(f"It was a normal day in {location} with " +
                ", ".join(f"{', '.join(characters[c]['traits'])} {c}" for c in present_characters[:-1]) +
                f" and {', '.join(characters[present_characters[-1]]['traits'])} {present_characters[-1]}.")

        if event:
            story_lines.append(f"Suddenly, {event}.")

        # Add specific character interactions
        if event == "fight" and len(present_characters) == 2:
            char1, char2 = present_characters
            story_lines.append(f"{char2} attacks {char1}. After a long fight, " +
                f"{', '.join(characters[char1]['traits'])} {char1} emerges victorious. "
                f"All the evil is defeated, and the world is happy again...")
    return "\n".join(story_lines)

def process_instruction(instruction_block):
    instruction_type = instruction_block.get("instruction", "")

    if instruction_type == "print characters":
        # Get the list of specified characters, if present
        specified_characters = instruction_block.get("characters", [])
        return "print characters", specified_characters

    elif instruction_type == "write story":
        return "write story", None

    else:
        return None, None

def main():
    parser = argparse.ArgumentParser(description="ArtLang story_generator.py")
    parser.add_argument("ast_file", help="Path to the AST input file")
    parser.add_argument("--output", "-o", required=True, help="Output file for the generated story")
    args = parser.parse_args()

    # Load AST
    with open(args.ast_file, 'r') as f:
        ast = json.load(f)

    # Get the instruction; instruction *must* be the last element in the AST
    instruction_block = ast[-1] 
    instruction = instruction_block.get("instruction", "")

    results = []

    # 'write story' instruction
    if instruction == "write story" or instruction == None:
        results.append("--- Story ---")
        results.append(generate_story(ast))

    # 'print characters' instruction
    if instruction == "print characters" or instruction == None:
        print("Instruction block:", instruction_block)  # Debug print
        characters = process_characters(ast[0])
        print("Processed characters:", characters)  # Debug print
        specified_characters = instruction_block.get("characters", [])
        print("Specified characters:", specified_characters)  # Debug print
        results.append("--- Character Details ---")
        results.append(print_characters_instruction(characters, specified_characters))

    # write output
    with open(args.output, 'w') as f:
        f.write("\n\n".join(results))
    print(f"Story successfully written to {args.output}")

if __name__ == "__main__":
    main()