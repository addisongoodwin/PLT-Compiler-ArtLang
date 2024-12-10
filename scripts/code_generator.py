import argparse
import json

def generate_code(ast):
    """
    Generate intermediate code from the AST.
    """
    code_lines = []

    for block in ast:
        if isinstance(block, list):  # Character block list
            for character in block:
                code_lines.append(f"# Character: {character['name']}")
                for detail in character.get("definition", []):
                    if detail["type"] == "restricted_assignment" and "evil" in detail:
                        evil_status = "True" if detail["evil"] else "False"
                        code_lines.append(f"SET EVIL {character['name']} {evil_status}")
                    elif detail["type"] == "restricted_assignment" and "strength" in detail:
                        code_lines.append(f"SET STRENGTH {character['name']} {detail['strength']}")
                    elif detail["type"] == "trait_list":
                        traits = ", ".join(detail["traits"])
                        code_lines.append(f"SET TRAITS {character['name']} {traits}")
                code_lines.append("")  # Blank line for readability
        
        elif isinstance(block, dict) and block["type"] == "scene_block_list":
            for scene in block.get("scenes", []):
                code_lines.append(f"# Scene: {scene['name']}")
                for detail in scene.get("details", []):
                    if detail["type"] == "location_assignment":
                        code_lines.append(f"SET LOCATION {scene['name']} {detail['location']}")
                    elif detail["type"] == "event_assignment":
                        code_lines.append(f"SET EVENT {scene['name']} \"{detail['event']}\"")
                    elif detail["type"] == "characters_present":
                        characters = ", ".join(detail["characters"])
                        code_lines.append(f"SET CHARACTERS {scene['name']} {characters}")
                code_lines.append("")  # Blank line for readability

        elif isinstance(block, dict) and block["type"] == "instruction_block":
            if block.get("content") == "write story":
                code_lines.append("WRITE_STORY")
            elif block.get("instruction") == "TOK_PRINT_CHARACTER_INST":
                code_lines.append("PRINT_CHARACTERS")

    return code_lines

def main():
    parser = argparse.ArgumentParser(description="Code Generator")
    parser.add_argument("ast_file", help="Path to the input AST JSON file")
    parser.add_argument(
        "--output", "-o", default="generated_code.txt",
        help="Path to the output file for the generated code"
    )
    args = parser.parse_args()

    # Read AST from JSON file
    with open(args.ast_file, "r") as infile:
        ast = json.load(infile)

    # Generate intermediate code
    code = generate_code(ast)

    # Write the code to an output file
    with open(args.output, "w") as outfile:
        outfile.write("\n".join(code))
        print(f"Code written to {args.output}")

if __name__ == "__main__":
    main()