import argparse
import os
import subprocess
import sys

PYTHON_EXECUTABLE = sys.executable

SCANNER_SCRIPT = os.path.abspath("scripts/my_scanner.py")
PARSER_SCRIPT = os.path.abspath("scripts/my_parser.py")
CODEGEN_SCRIPT = os.path.abspath("scripts/code_generator.py")

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
    for script in [SCANNER_SCRIPT, PARSER_SCRIPT, CODEGEN_SCRIPT]:
        if not os.path.exists(script):
            raise FileNotFoundError(f"Script not found: {script}")

    # Step 1: Set up the output directory
    output_folder = os.path.abspath(args.output_folder)
    os.makedirs(output_folder, exist_ok=True)
    print(f"All outputs will be stored in: {output_folder}")

    # File paths for intermediaries
    tokens_file = os.path.join(output_folder, "tokens.txt")
    ast_file = os.path.join(output_folder, "ast.json")
    final_code_file = os.path.join(output_folder, "generated_code.txt")

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

    # Step 4: Run the code generator
    print("\n--- Running Code Generator ---")
    codegen_command = [PYTHON_EXECUTABLE, CODEGEN_SCRIPT, ast_file, "--output", final_code_file]
    stdout, stderr = run_command(codegen_command)
    print(f"Generated code written to: {final_code_file}")

    # Final message
    print("\n--- Pipeline Complete ---")
    print(f"Written to '{output_folder}' :")
    print(f"- Tokens: {tokens_file}")
    print(f"- AST: {ast_file}")
    print(f"- Final Code: {final_code_file}") ## NOT FINAL CODE!!!!~~~~~~~~~~~~~~~~~~~~~~~~
    print("Enjoy :)")

if __name__ == "__main__":
    main()