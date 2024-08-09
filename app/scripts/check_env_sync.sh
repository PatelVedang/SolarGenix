#!/bin/bash

# Define the paths to the .env and .env_example files
ENV_FILE="app/.env"
ENV_EXAMPLE_FILE="app/.env_example"

# Function to compare two files ignoring comment and empty lines
compare_files() {
  # Filter out comment and empty lines, then compare
  diff_output=$(diff <(grep -v '^\s*#' "$ENV_FILE" | grep -v '^\s*$' | sort) <(grep -v '^\s*#' "$ENV_EXAMPLE_FILE" | grep -v '^\s*$' | sort))
  
  if [ "$diff_output" != "" ]; then
    echo "ERROR: $ENV_FILE and $ENV_EXAMPLE_FILE have different values. Please synchronize them before committing."
    echo "Differences found:"
    echo "$diff_output"
    exit 1
  fi
}

# Check if both files exist
if [ ! -f "$ENV_FILE" ] || [ ! -f "$ENV_EXAMPLE_FILE" ]; then
  echo "ERROR: Either $ENV_FILE or $ENV_EXAMPLE_FILE is missing."
  exit 1
fi

# Compare the files ignoring comment and empty lines
compare_files

# Allow the commit if files match
exit 0
