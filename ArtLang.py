import argparse
import os
import subprocess
import sys

PYTHON_EXECUTABLE = sys.executable

SCANNER_SCRIPT = os.path.abspath("scripts/my_scanner.py")
PARSER_SCRIPT = os.path.abspath("scripts/my_parser.py")
STORYGEN_SCRIPT = os.path.abspath("scripts/story_generator.py")

def run_command(command, working_dir=None):
    try:
        result = subprocess.run(
            command, 
            cwd=working_dir, 
            capture_output=True, 
            text=True, 
            check=True  # This will raise CalledProcessError if returncode is non-zero
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(f"Error output: {e.stderr}")
        print(f"Return code: {e.returncode}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Addison compilation pipeline")
    parser.add_argument("input_file", help="Path to the program input file")
    parser.add_argument(
        "--output_folder", "-o", required=True,
        help="Folder name to store all intermediary and output files"
    )
    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input_file):
        raise FileNotFoundError(f"Input file not found: {args.input_file}")

    # Validate script files exist
    for script in [SCANNER_SCRIPT, PARSER_SCRIPT, STORYGEN_SCRIPT]:
        if not os.path.exists(script):
            raise FileNotFoundError(f"Script not found: {script}")

    # Step 1: Set up the output directory
    output_folder = os.path.abspath(args.output_folder)
    os.makedirs(output_folder, exist_ok=True)
    print(f"All outputs will be stored in: {output_folder}")

    # File paths for intermediaries
    tokens_file = os.path.join(output_folder, "tokens.txt")
    ast_file = os.path.join(output_folder, "ast.json")
    story_output_file = os.path.join(output_folder, "story.txt")

    # Step 2: Run the scanner
    print("\n--- Running Scanner ---")
    scanner_command = [PYTHON_EXECUTABLE, SCANNER_SCRIPT, args.input_file, "--output", tokens_file]
    stdout, stderr = run_command(scanner_command)
    print(f"Tokens written to: {tokens_file}")

    # Step 3: Run the parser
    print("\n--- Running Parser ---")
    parser_command = [PYTHON_EXECUTABLE, PARSER_SCRIPT, tokens_file, "--output", ast_file]
    stdout, stderr = run_command(parser_command)
    print(f"AST written to: {ast_file}")

    # Step 4: Run the story generator
    print("\n--- Running Story Generator ---")
    if not os.path.exists(STORYGEN_SCRIPT):
        raise FileNotFoundError(f"Script not found: {STORYGEN_SCRIPT}")

    # story_output_file = os.path.join(output_folder, "story_output.txt")
    storygen_command = [PYTHON_EXECUTABLE, STORYGEN_SCRIPT, ast_file, "--output", story_output_file]
    stdout, stderr = run_command(storygen_command)
    print(f"Story output written to: {story_output_file}")

    # Final message
    print("\n--- Pipeline Complete ---")
    print(f"Written to '{output_folder}' :")
    print(f"- Tokens: {tokens_file}")
    print(f"- AST: {ast_file}")
    print(f"- Story: {story_output_file}")
    print("Enjoy :)")

if __name__ == "__main__":
    main()