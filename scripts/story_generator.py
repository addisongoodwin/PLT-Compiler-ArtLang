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
        for detail in block["definition"]:
            if detail["type"] == "trait_list":
                traits.extend(detail["traits"])
            elif detail["type"] == "restricted_assignment":
                if "evil" in detail:
                    evil = detail["evil"]
        characters[name] = {"traits": traits, "evil": evil}
    return characters

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

def main():
    parser = argparse.ArgumentParser(description="Story Generator")
    parser.add_argument("ast_file", help="Path to the AST input file")
    parser.add_argument("--output", "-o", required=True, help="Output file for the generated story")
    args = parser.parse_args()

    # Load AST
    with open(args.ast_file, 'r') as f:
        ast = json.load(f)

    # Generate story
    story = generate_story(ast)

    # Write output to file
    with open(args.output, 'w') as f:
        f.write(story)
    print(f"Story successfully written to {args.output}")

if __name__ == "__main__":
    main()