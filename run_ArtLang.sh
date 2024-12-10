#!/bin/bash

# Ensure the script exits if any command fails
set -e

declare -a tests=(
    "sample_code/test1.txt test1"
    "sample_code/test2_unrecognized_chars.txt test2"
    "sample_code/test3_long_prchr.txt test3_prchr"
    "sample_code/test3_long.txt test3_story"
    "sample_code/test4_errors.txt test4"
    "sample_code/test5_weird_vals_prchr.txt test5_prchr"
    "sample_code/test5_weird_vals.txt test5_story"
)

# Loop through the tests and run pipeline.py
for test in "${tests[@]}"; do
    # Split the test into input and output
    read -r input_file output_folder <<< "$test"
    
    echo "Running ArtLang.py on $input_file with output folder $output_folder..."

    # Run the pipeline.py script
    python ArtLang.py "$input_file" --output_folder "$output_folder"

    # Check if the command was successful
    if [ $? -eq 0 ]; then
        echo "Test $input_file completed successfully. Results stored in $output_folder."
    else
        echo "Test $input_file encountered an error."
    fi

    echo "-----------------------------------------------"
done

echo "All tests have been executed."