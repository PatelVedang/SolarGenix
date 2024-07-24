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
example_env_path="app/.env_example"
env_path="app/.env"
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

echo "Set executable permiossion to the rest generator"
echo "----------------------------------------------------"
sudo chmod +x app/rest_generator.sh
echo "----------------------------------------------------"
printf "Executable permission set to rest generator 😎 \n\n\n"


echo "Installing JQ"
echo "----------------------------------------------------"
if ! is_command_available jq; then
    sudo apt-get install jq -y || ( echo "Failed to install JQ" && exit 1 )
else
    echo "JQ is already installed. Skipping installation."
fi
echo "----------------------------------------------------"
printf "JQ Installed 😎 \n\n\n"

echo "Installing Postgres Database"
echo "----------------------------------------------------"

# Install PostgreSQL
echo "Installing PostgreSQL..."
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# Get username, password, and database name
read -p "Enter the new user name: " new_user
echo "New User: $new_user"
read -s -p "Enter the password for the new user: " new_password
echo -e " "
read -p "Enter the database name: " new_db
echo -e "New Database: $new_db"


# Create user with password
echo "Creating a new PostgreSQL user..."
sudo -i -u postgres psql -c "CREATE USER $new_user WITH PASSWORD '$new_password';"

# Create new database and assign privileges
echo "Creating a new database and assigning privileges to the new user..."
sudo -i -u postgres psql -c "CREATE DATABASE $new_db;"
sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $new_db TO $new_user;"

# Altering the schema owner
echo "Altering the schema owner..."
sudo -i -u postgres psql -d "$new_db" -c "ALTER SCHEMA public OWNER TO $new_user;"

# Find the PostgreSQL version dynamically
postgres_version=$(ls /etc/postgresql/ | grep -E '^[0-9]+$' | tail -n 1)

# Configuring PostgreSQL for remote access
if [ -n "$postgres_version" ]; then
    # Use the specific version in the path
    echo "listen_addresses = '*'" | sudo tee -a "/etc/postgresql/$postgres_version/main/postgresql.conf"
    echo "host all all 0.0.0.0/0 md5" | sudo tee -a "/etc/postgresql/$postgres_version/main/pg_hba.conf"

    # Restarting PostgreSQL to apply changes
    echo "Restarting PostgreSQL..."
    sudo service postgresql restart
    echo "Remote access granted for new database ..."
else
    echo "Error: Unable to determine PostgreSQL version."
fi

echo "----------------------------------------------------"
printf "Postgres installed, new database created and successfully assign the privileges to user for new database 😎 \n\n\n"

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
