#!/usr/bin/env bash

#clear the screen
clear
echo " "
echo " "
echo " "
echo "  ____      _                    _                _ _                      "
echo " / ___|   _| |__   ___ _ __     / \   _ __  _ __ | (_) __ _ _ __   ___ ___ "
echo "| |  | | | | '_ \ / _ \ '__|   / _ \ | '_ \| '_ \| | |/ _\` | '_ \ / __/ _ \\"
echo "| |__| |_| | |_) |  __/ |     / ___ \| |_) | |_) | | | (_| | | | | (_|  __/"
echo " \____\__, |_.__/ \___|_|    /_/   \_\ .__/| .__/|_|_|\__,_|_| |_|\___\___|"
echo "      |___/                          |_|   |_|                             "
echo " "
echo " "
echo " "


# Function to check if a package is installed using dpkg
function is_package_installed() {
    dpkg -l "$1" &> /dev/null
}

# Function to check if a command (tool) is available in the system's PATH
function is_command_available() {
    command -v "$1" &> /dev/null
}

# Create the file and write the dynamic content into it using a here document
example_env_path="app/proj/.env_example"
filepath="app/proj/.env"
cat "$example_env_path" > "$filepath"

echo "File '$filepath' created with the following content:"
echo "----------------------------------------------------"
cat "$filepath"
printf "\n----------------------------------------------------\n\n\n"

echo "Downloading package information from all configured sources"
echo "----------------------------------------------------"
sudo apt-get update -y || ( echo "Failed to update package information" && exit 1 )
echo "----------------------------------------------------"
printf "Package information Downloaded 😎 \n\n\n"

echo "Installing Nmap"
echo "----------------------------------------------------"
if ! is_command_available nmap; then
    sudo apt-get install nmap -y || ( echo "Failed to install Nmap" && exit 1 )
else
    echo "Nmap is already installed. Skipping installation."
fi
echo "----------------------------------------------------"
printf "Nmap Installed 😎 \n\n\n"

echo "Installing wkhtmltopdf for pdfkit"
echo "----------------------------------------------------"
if ! is_command_available wkhtmltopdf; then
    sudo apt-get install wkhtmltopdf -y || ( echo "Failed to install wkhtmltopdf" && exit 1 )
else
    echo "wkhtmltopdf is already installed. Skipping installation."
fi
echo "----------------------------------------------------"
printf "wkhtmltopdf Installed 😎 \n\n\n"

echo "Installing MySQL Server"
echo "----------------------------------------------------"
if ! is_command_available mysql; then
    sudo apt-get install mysql-server -y || ( echo "Failed to install MySQL Server" && exit 1 )
else
    echo "MySQL Server is already installed. Skipping installation."
fi
echo "----------------------------------------------------"
printf "MySQL Server Installed 😎 \n\n\n"

# Prompt the user to enter test database and test user names
read -p "Enter the database name for this server: " db
read -p "Enter the username for databse $db: " db_user
# Prompt the user to enter the test user password (hiding input for security)
read -s -p "Enter the password for $db_user user to access $db database: " db_password
echo ""

# Create the test database and test user, and grant full access to the test database for all hosts
sudo mysql -uroot -e "CREATE DATABASE IF NOT EXISTS $db;"
sudo mysql -uroot -e "CREATE USER IF NOT EXISTS '$db_user'@'%' IDENTIFIED BY '$db_password';"
sudo mysql -uroot -e "GRANT ALL PRIVILEGES ON $db.* TO '$db_user'@'%';"
sudo mysql -uroot -e "FLUSH PRIVILEGES;"
echo "----------------------------------------------------"
printf "Test database and user created 😎 \n\n\n"


echo "Installing MySQL development headers"
echo "----------------------------------------------------"
if ! is_package_installed python3-dev; then
    sudo apt-get install python3-dev -y || ( echo "Failed to install python3-dev in MySQL development headers." && exit 1 )
else
    echo "python3-dev is already installed in MySQL development headers. Skipping installation python3-dev."
fi
if ! is_package_installed default-libmysqlclient-dev; then
    sudo apt-get install default-libmysqlclient-dev -y || ( echo "Failed to install default-libmysqlclient-dev in MySQL development headers." && exit 1 )
else
    echo "default-libmysqlclient-dev is already installed in MySQL development headers. Skipping installation default-libmysqlclient-dev."
fi
if ! is_package_installed build-essential; then
    sudo apt-get install build-essential -y || ( echo "Failed to install build-essential in MySQL development headers." && exit 1 )
else
    echo "build-essential is already installed in MySQL development headers. Skipping installation build-essential."
fi
echo "----------------------------------------------------"
printf "MySQL development headers Installed 😎 \n\n\n"

echo "Installing rabbitmq-server"
echo "----------------------------------------------------"
if ! is_command_available rabbitmq-server; then
    sudo apt-get install rabbitmq-server -y || ( echo "Failed to install RabbitMQ" && exit 1 )
    sudo systemctl start rabbitmq-server
    sudo systemctl enable rabbitmq-server
else
    echo "Redis server is already installed. Skipping installation."
    sudo systemctl start rabbitmq-server
    sudo systemctl enable rabbitmq-server
    echo "RabbitMQ is already installed. Skipping installation."
fi
# echo "----------------------------------------------------"
# printf "RabbitMQ Installed 😎 \n\n\n"

# echo "Installing redis-server"
# echo "----------------------------------------------------"
# if ! is_command_available Redis server; then
#     sudo apt-get install redis-server -y || ( echo "Failed to install Redis server" && exit 1 )
#     # Start and enable the service
#     sudo systemctl start redis-server
#     sudo systemctl enable redis-server
# else
#     echo "Redis server is already installed. Skipping installation."
#     sudo systemctl start redis-server
#     sudo systemctl enable redis-server
# fi
echo "----------------------------------------------------"
printf "Redis Server Has Been Installed And Started 😎 \n\n\n"

echo "Installing OWASP_ZAP server"
echo "----------------------------------------------------"
if ! is_command_available zap.sh; then
    sudo apt update -y
    sudo apt install default-jdk -y
    sudo apt install default-jre -y
    wget https://github.com/zaproxy/zaproxy/releases/download/v2.12.0/ZAP_2_12_0_unix.sh
    sudo chmod +x ZAP_2_12_0_unix.sh
    sudo bash ZAP_2_12_0_unix.sh
    sudo rm ZAP_2_12_0_unix.sh
else
    echo "OWASP_ZAP server is already installed. Skipping installation."
fi
echo "----------------------------------------------------"
printf "OWASP_ZAP server Installed 😎 \n\n\n"

echo "Installing PM2 with NVM"
echo "----------------------------------------------------"
if ! is_command_available pm2; then
    curl https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash
    source ~/.bashrc
    nvm install latest
    npm install pm2 -g
else
    echo "PM2 with NVM is already installed. Skipping installation."
fi
echo "----------------------------------------------------"
printf "PM2 with NVM Installed 😎 \n\n\n"

# Check if virtualenv is available, else install python3-venv
echo "Checking virtualenv installation"
echo "----------------------------------------------------"
if ! is_command_available virtualenv; then
    sudo apt-get install python3-venv -y || ( echo "Failed to install python3-venv" && exit 1 )
else
    echo "virtualenv is already installed. Skipping installation."
fi
echo "----------------------------------------------------"
printf "virtualenv installation checked 😎 \n\n\n"

echo "Creating Virtual Environment"
echo "----------------------------------------------------"
if [ ! -d "env" ]; then
    python3 -m venv env
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
printf "░░░░░░  Now U have to provide the exact value in $filepath And run the below files. ░░░░░░\n"
printf "░░░░░░  apply_migrations.sh - Applying the migrations                                   ░░░░░░\n"
printf "░░░░░░  server.sh - Run server                                                          ░░░░░░\n"
printf "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░\n"

# Wait for user input before exiting the script
read -n 1 -s -r -p "Press any key to leave..."
echo " "
