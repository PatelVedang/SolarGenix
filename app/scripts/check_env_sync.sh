#!/bin/bash

# Define the paths to the .env and .env_example files
ENV_FILE="app/.env"
ENV_EXAMPLE_FILE="app/.env_example"

# Function to compare keys between two files ignoring comment and empty lines
compare_keys() {
  # Extract keys, filter out comment and empty lines, and sort them
  keys_env_file=$(grep -v '^\s*#' "$ENV_FILE" | grep -v '^\s*$' | cut -d '=' -f 1 | sort)
  keys_env_example_file=$(grep -v '^\s*#' "$ENV_EXAMPLE_FILE" | grep -v '^\s*$' | cut -d '=' -f 1 | sort)

  # Compare the sorted keys and capture the differences
  diff_output=$(diff <(echo "$keys_env_file") <(echo "$keys_env_example_file"))

  # Variables to store the missing keys
  missing_in_env=()
  missing_in_env_example=()

  # Process the diff output and categorize the missing keys
  while read -r line; do
    if [[ $line == "<"* ]]; then
      missing_in_env+=("${line#< }")
    elif [[ $line == ">"* ]]; then
      missing_in_env_example+=("${line#> }")
    fi
  done <<< "$diff_output"

  # Display the differences with clear formatting
  if [ "${#missing_in_env[@]}" -ne 0 ] || [ "${#missing_in_env_example[@]}" -ne 0 ]; then
    echo "ERROR: The keys in $ENV_FILE and $ENV_EXAMPLE_FILE are different. Please synchronize them before committing."
    echo
    echo "Differences in keys found:"
    echo "-------------------------"
    
    # Display keys missing in .env
    if [ "${#missing_in_env[@]}" -ne 0 ]; then
      echo "Keys missing in .env:"
      for key in "${missing_in_env[@]}"; do
        echo "  - $key"
      done
      echo
    fi
    
    # Display keys missing in .env_example
    if [ "${#missing_in_env_example[@]}" -ne 0 ]; then
      echo "Keys missing in .env_example:"
      for key in "${missing_in_env_example[@]}"; do
        echo "  - $key"
      done
    fi

    echo "-------------------------"
    exit 1
  fi
}

# Check if both files exist
if [ ! -f "$ENV_FILE" ] || [ ! -f "$ENV_EXAMPLE_FILE" ]; then
  echo "ERROR: Either $ENV_FILE or $ENV_EXAMPLE_FILE is missing."
  exit 1
fi

# Compare the keys between the files
compare_keys

# Allow the commit if keys match
exit 0