#!/usr/bin/env bash

# Function to check if a package is installed (Linux)
function is_package_installed_linux() {
    dpkg -l "$1" &> /dev/null
}

# Function to check if a command (tool) is available
function is_command_available() {
    command -v "$1" &> /dev/null
}

# Function to check if a package is installed (macOS)
function is_package_installed_mac() {
    brew list --versions "$1" &> /dev/null
}

# Clear the screen
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

# Determine OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo "Unsupported OS."
    exit 1
fi

# Ask user if they want to create the .env file
read -p "Do you want to create a new .env file from .env_example? (y/n): " create_env

if [ "$create_env" == "y" ]; then
    example_env_path="app/.env_example"
    env_path="app/.env"
    
    if [ -f "$example_env_path" ]; then
        cat "$example_env_path" > "$env_path"
        echo "File '$env_path' created with the following content:"
        echo "----------------------------------------------------"
        cat "$env_path"
        echo "----------------------------------------------------"
    else
        echo "Example environment file '$example_env_path' does not exist. Skipping creation of '$env_path'."
    fi
else
    echo "Skipping .env file creation."
fi

echo "Downloading package information from all configured sources"
echo "----------------------------------------------------"
if [ "$OS" == "linux" ]; then
    sudo apt-get update -y || ( echo "Failed to update package information" && exit 1 )
elif [ "$OS" == "mac" ]; then
    brew update || ( echo "Failed to update package information" && exit 1 )
fi
echo "----------------------------------------------------"
printf "Package information Downloaded 😎 \n\n\n"

echo "Set executable permission to the rest generator"
echo "----------------------------------------------------"
sudo chmod +x app/rest_generator.sh
echo "----------------------------------------------------"
printf "Executable permission set to rest generator 😎 \n\n\n"

echo "Installing JQ"
echo "----------------------------------------------------"
if ! is_command_available jq; then
    if [ "$OS" == "linux" ]; then
        sudo apt-get install jq -y || ( echo "Failed to install JQ" && exit 1 )
    elif [ "$OS" == "mac" ]; then
        brew install jq || ( echo "Failed to install JQ" && exit 1 )
    fi
else
    echo "JQ is already installed. Skipping installation."
fi
echo "----------------------------------------------------"
printf "JQ Installed 😎 \n\n\n"

echo "Installing Ruff VS Code Extension"
echo "----------------------------------------------------"
if is_command_available code; then
    # Check if the Ruff extension is already installed
    if ! code --list-extensions | grep -q "charliermarsh.ruff"; then
        echo "Ruff extension not found. Installing..."
        if code --install-extension charliermarsh.ruff; then
            echo "Ruff extension installed successfully."
        else
            echo "Failed to install the Ruff extension. Please check the error messages above."
            exit 1
        fi
    else
        echo "Ruff extension is already installed. Skipping installation."
    fi
else
    echo "Visual Studio Code is not installed or the 'code' command is not available in your PATH."
    echo "Please install Visual Studio Code and make sure the 'code' command is available."
    exit 1
fi
echo "----------------------------------------------------"
printf "Ruff VS Code Extension Installation Completed 😎 \n\n\n"


echo "Installing Postgres Database"
echo "----------------------------------------------------"

# Ask user if they want to create a new PostgreSQL user and database
read -p "Do you want to create a new PostgreSQL user and database? (y/n): " create_db

if [ "$create_db" == "y" ]; then
    if [ "$OS" == "linux" ]; then
        echo "Installing PostgreSQL..."
        echo "----------------------------------------------------"
        if is_package_installed_linux postgresql; then
            echo "PostgreSQL is already installed. Skipping installation."
        else
            sudo apt-get install -y postgresql postgresql-contrib || ( echo "Failed to install PostgreSQL" && exit 1 )
        fi
        echo "----------------------------------------------------"
    elif [ "$OS" == "mac" ]; then
        echo "Installing PostgreSQL..."
        echo "----------------------------------------------------"
        if is_package_installed_mac postgresql; then
            echo "PostgreSQL is already installed. Skipping installation."
        else
            brew install postgresql || ( echo "Failed to install PostgreSQL" && exit 1 )
        fi
        echo "----------------------------------------------------"
    fi

    echo "Creating a new PostgreSQL user and database"
    echo "----------------------------------------------------"
    
    read -p "Enter the new user name: " new_user
    echo "New User: $new_user"
    read -s -p "Enter the password for the new user: " new_password
    echo -e " "
    read -p "Enter the database name: " new_db
    echo -e "New Database: $new_db"

    echo "Creating a new PostgreSQL user..."
    if [ "$OS" == "linux" ]; then
        sudo -i -u postgres psql -c "CREATE USER $new_user WITH PASSWORD '$new_password';"
    elif [ "$OS" == "mac" ]; then
        createuser -P "$new_user"
    fi

    echo "Creating a new database and assigning privileges to the new user..."
    if [ "$OS" == "linux" ]; then
        sudo -i -u postgres psql -c "CREATE DATABASE $new_db;"
        sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $new_db TO $new_user;"
        echo "Altering the schema owner..."
        sudo -i -u postgres psql -d "$new_db" -c "ALTER SCHEMA public OWNER TO $new_user;"
        # Allow user to create db
        sudo -i -u postgres psql -c "ALTER USER $new_user CREATEDB;"
    elif [ "$OS" == "mac" ]; then
        createdb "$new_db"
        psql -c "GRANT ALL PRIVILEGES ON DATABASE $new_db TO $new_user;"
        # Allow user to create db
        psql -c "ALTER USER $new_user CREATEDB;"
    fi

    # Configure PostgreSQL for remote access
    if [ "$OS" == "linux" ]; then
        postgres_version=$(ls /etc/postgresql/ | grep -E '^[0-9]+$' | tail -n 1)
        if [ -n "$postgres_version" ]; then
            postgres_conf="/etc/postgresql/$postgres_version/main/postgresql.conf"
            pg_hba_conf="/etc/postgresql/$postgres_version/main/pg_hba.conf"
            if ! sudo grep -q "^listen_addresses = '*'" "$postgres_conf"; then
                echo "Setting listen_addresses..."
                echo "listen_addresses = '*'" | sudo tee -a "$postgres_conf"
            else
                echo "listen_addresses is already set to '*'"
            fi
            if ! sudo grep -q "^host all all 0.0.0.0/0 md5" "$pg_hba_conf"; then
                echo "Setting host access..."
                echo "host all all 0.0.0.0/0 md5" | sudo tee -a "$pg_hba_conf"
            else
                echo "host access is already set"
            fi
            echo "Restarting PostgreSQL..."
            sudo service postgresql restart
        else
            echo "Error: Unable to determine PostgreSQL version."
        fi
    elif [ "$OS" == "mac" ]; then
        echo "PostgreSQL configuration for remote access is typically managed via `pgAdmin` or other tools."
        echo "Please ensure that remote access is configured as needed."
    fi

    echo "----------------------------------------------------"
    printf "Postgres User and Database Created 😎 \n\n\n"
else
    echo "Skipping PostgreSQL user and database creation."
fi

# Required Python version
PYTHON_REQUIRED_VERSION="3.11"
echo "Checking Python $PYTHON_REQUIRED_VERSION"
echo "----------------------------------------------------"

# Check if python3.11 is available and its version
if is_command_available "python$PYTHON_REQUIRED_VERSION"; then
    python_version=$( "python$PYTHON_REQUIRED_VERSION" --version 2>&1 )
    if [[ $python_version == *"$PYTHON_REQUIRED_VERSION"* ]]; then
        echo "Python $python_version is already installed."
    else
        echo "Installed Python version does not match $PYTHON_REQUIRED_VERSION. Found: $python_version"
        INSTALL_PYTHON=true
    fi
else
    echo "Python $PYTHON_REQUIRED_VERSION is not installed. Installing..."
    INSTALL_PYTHON=true
fi

if [ "$INSTALL_PYTHON" = true ]; then
    if [ "$OS" == "linux" ]; then
        sudo apt update
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt install "python$PYTHON_REQUIRED_VERSION" -y
    elif [ "$OS" == "mac" ]; then
        brew install "python@$PYTHON_REQUIRED_VERSION"
    fi
    
    if is_command_available "python$PYTHON_REQUIRED_VERSION"; then
        python_version=$( "python$PYTHON_REQUIRED_VERSION" --version 2>&1 )
        if [[ $python_version == *"$PYTHON_REQUIRED_VERSION"* ]]; then
            echo "Python $python_version installed successfully."
        else
            echo "Failed to install Python $PYTHON_REQUIRED_VERSION. Please check the installation manually."
            exit 1
        fi
    else
        echo "Failed to install Python $PYTHON_REQUIRED_VERSION. Please check the installation manually."
        exit 1
    fi
fi
echo "----------------------------------------------------"
printf "Python 3.11 check and installation completed 😎 \n\n\n"

echo "Installing Python 3.11 venv module"
echo "----------------------------------------------------"
if [ "$OS" == "linux" ]; then
    sudo apt install "python$PYTHON_REQUIRED_VERSION-venv" -y
fi
echo "----------------------------------------------------"
printf "Python 3.11 venv module Installed 😎 \n\n\n"

echo "Creating Virtual Environment"
echo "----------------------------------------------------"
if [ ! -d "env" ]; then
    "python$PYTHON_REQUIRED_VERSION" -m venv env
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

echo "Install pre-commit hooks"
echo "----------------------------------------------------"
pre-commit install 
pre-commit install --hook-type commit-msg
echo "----------------------------------------------------"
printf "Pre-commit hooks installed 😎 \n\n\n"

echo "Deactivating virtual Environment"
echo "----------------------------------------------------"
deactivate
echo "----------------------------------------------------"
printf "Virtual Environment Deactivated 😎 \n\n\n"

printf "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░\n"
if [ "$create_env" == "y" ]; then
    printf "░░░░░░  Now U have to provide the exact value in $env_path And run the below files. ░░░░░░\n"
fi
printf "░░░░░░  apply_migrations.sh - Applying the migrations                                   ░░░░░░\n"
printf "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░\n"

# Wait for user input before exiting the script
read -n 1 -s -r -p "Press any key to leave..."
echo " "