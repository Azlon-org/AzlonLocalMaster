#!/bin/bash

# Default values for the demo
DEFAULT_DATA_DIR="multi_agents/competition/CarWash_Data"
# Attempt to find a common context file name, can be made more robust later
DEFAULT_CONTEXT_FILENAMES=("bussiness_description.txt" "business_context.txt" "readme.txt" "context.txt")
MODEL_NAME="gpt-4.1-mini" # Or make this an argument if needed for the demo

# Use provided data directory or default
DATA_DIR=${1:-$DEFAULT_DATA_DIR}

# Attempt to find the context file in the data directory
CONTEXT_FILE=""
for filename in "${DEFAULT_CONTEXT_FILENAMES[@]}"; do
    if [ -f "$DATA_DIR/$filename" ]; then
        CONTEXT_FILE="$DATA_DIR/$filename"
        break
    fi
done

# --- Sanity Checks ---
# Check if data directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo "Error: Data directory '$DATA_DIR' not found."
    echo "Usage: $0 [path_to_data_directory]"
    exit 1
fi

# Check if context file was found
if [ -z "$CONTEXT_FILE" ]; then
    echo "Error: Could not find a context file in '$DATA_DIR'. Looked for: ${DEFAULT_CONTEXT_FILENAMES[*]}"
    exit 1
fi

echo "-------------------------------------------------"
echo "Starting Business Insight Generation Demo"
echo "-------------------------------------------------"
echo "Data Directory: $DATA_DIR"
echo "Context File  : $CONTEXT_FILE"
echo "Model         : $MODEL_NAME"
echo "-------------------------------------------------"

# Run framework.py
python3 framework.py --data_dir "$DATA_DIR" --context_file "$CONTEXT_FILE" --model "$MODEL_NAME"

EXIT_CODE=$?

echo "-------------------------------------------------"
if [ $EXIT_CODE -eq 0 ]; then
    echo "Demo script finished successfully."
    echo "Check for analysis.log in $DATA_DIR"
else
    echo "Demo script encountered an error (Exit Code: $EXIT_CODE)."
fi
echo "-------------------------------------------------"

exit $EXIT_CODE