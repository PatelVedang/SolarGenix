#!/usr/bin/env bash

# Function to check if a package is installed using dpkg
function is_package_installed() {
    dpkg -l "$1" &> /dev/null
}

# Function to check if a command (tool) is available in the system's PATH
function is_command_available() {
    command -v "$1" &> /dev/null
}

#clear the screen
clear
echo " ____  _                         "
echo "|  _ \\(_) __ _ _ __   __ _  ___  "
echo "| | | | |/ _\` | '_ \\ / _\` |/ _ \\ "
echo "| |_| | | (_| | | | | (_| | (_) |"
echo "|____// |\\__,_|_| |_|\\__, |\\___/ "
echo "    |__/             |___/       "
echo " ____        _ _                 _       _       "
echo "| __ )  ___ (_) | ___ _ __ _ __ | | __ _| |_ ___ "
echo "|  _ \\ / _ \\| | |/ _ \\ '__| '_ \\| |/ _\` | __/ _ \\"
echo "| |_) | (_) | | |  __/ |  | |_) | | (_| | ||  __/"
echo "|____/ \\___/|_|_|\\___|_|  | .__/|_|\\__,_|\\__\\___|"
echo "                          |_|                    "



# Create the file and write the dynamic content into it using a here document
example_env_path=".env_example"
env_path=".env"
cat "$example_env_path" > "$env_path"

echo "File '$env_path' created with the following content:"
echo "----------------------------------------------------"
cat "$env_path"
printf "\n----------------------------------------------------\n\n\n"

echo "Downloading package information from all configured sources"
echo "----------------------------------------------------"
sudo apt-get update -y || ( echo "Failed to update package information" && exit 1 )
echo "----------------------------------------------------"
printf "Package information Downloaded 😎 \n\n\n"

echo "Checking Python 3.11"
echo "----------------------------------------------------"
python_version=$(python3.11 --version 2>&1)
if [[ $python_version == *"3.11"* ]]; then
    echo "Python 3.11 is already installed."
else
    echo "Python 3.11 is not installed. Installing..."
    # Update package index
    sudo apt update
    # Install Python 3 and python3.11-venv
    sudo apt install python3 python3.11-venv -y
    # Verify installation
    python_version=$(python3.11 --version 2>&1)
    if [[ $python_version == *"3.11"* ]]; then
        echo "Python 3.11 installed successfully."
    else
        echo "Failed to install Python 3.11. Please check the installation manually."
        exit 1
    fi
fi
echo "----------------------------------------------------"
printf "Python 3.11 check and installation completed 😎 \n\n\n"

echo "Creating Virtual Environment"
echo "----------------------------------------------------"
if [ ! -d "env" ]; then
    python3.11 -m venv env
else
    echo "Virtual Environment already exists. Skipping creation."
fi
echo "----------------------------------------------------"
printf "Virtual env Created 😎 \n\n\n"

echo "Activating Virtual Environment"
echo "----------------------------------------------------"
source env/bin/activate
echo "----------------------------------------------------"
printf "Virtual env activated 😎 \n\n\n"

echo "Installing python level dependencies"
echo "----------------------------------------------------"
pip install -r app/requirements.txt || ( echo "Failed to install python level dependencies" && exit 1 )
echo "----------------------------------------------------"
printf "python level dependencies Installed 😎 \n\n\n"

echo "Deactivating virtual Enviroment"
echo "----------------------------------------------------"
deactivate
echo "----------------------------------------------------"
printf "Virtual Enviroment Deactivated 😎 \n\n\n"

printf "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░\n"
printf "░░░░░░  Now U have to provide the exact value in $env_path And run the below files. ░░░░░░\n"
printf "░░░░░░  apply_migrations.sh - Applying the migrations                                   ░░░░░░\n"
printf "░░░░░░  server.sh - Run server                                                          ░░░░░░\n"
printf "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░\n"

# Wait for user input before exiting the script
read -n 1 -s -r -p "Press any key to leave..."
echo " "
