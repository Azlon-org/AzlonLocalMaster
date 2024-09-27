#!/bin/bash

# Default values
# "titanic" "spaceship_titanic" 
competitions=("ghouls_goblins_and_ghosts_boo" "bank_churn" "classification_with_an_academic_success_dataset")
runs=2

# Function to run a single experiment
run_experiment() {
    competition=$1
    run_number=$2

    echo "Running $competition - Experiment $run_number"

    # Run framework.py
    python framework.py --competition "$competition"

    # Define source and destination directories
    source_dir="multi_agents/competition/$competition"
    dest_dir="multi_agents/experiments_history/$competition/tool_data_cleaning/$run_number"

    # Create destination directory if it doesn't exist
    mkdir -p "$dest_dir"

    # Move files and directories
    for item in "$source_dir"/*; do
        filename=$(basename "$item")
        if [[ "$filename" != "overview.txt" && "$filename" != "sample_submission.csv" && "$filename" != "test.csv" && "$filename" != "train.csv" && "$filename" != "data_description.txt" ]]; then
            if [ -d "$item" ]; then
                # If it's a directory, copy it recursively
                cp -R "$item" "$dest_dir/"
                rm -rf "$item"
            else
                # If it's a file, move it
                mv "$item" "$dest_dir/"
            fi
        fi
    done
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --competitions)
        IFS=' ' read -r -a competitions <<< "$2"
        shift
        shift
        ;;
        --runs)
        runs="$2"
        shift
        shift
        ;;
        *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Run experiments for each competition
for competition in "${competitions[@]}"; do
    for ((run=1; run<=runs; run++)); do
        run_experiment "$competition" "$run"
    done
done

echo "All experiments completed."