# Function to check if a package is installed (Windows)
function Is-PackageInstalled {
    param (
        [string]$packageName
    )
    Get-Package -Name $packageName -ErrorAction SilentlyContinue
}

# Function to check if a command (tool) is available
function Is-CommandAvailable {
    param (
        [string]$command
    )
    Get-Command $command -ErrorAction SilentlyContinue
}

# Clear the screen
Clear-Host
Write-Host " ____  _                         "
Write-Host "|  _ \(_) __ _ _ __   __ _  ___  "
Write-Host "| | | | |/ _` | '_ \ / _` |/ _ \ "
Write-Host "| |_| | | (_| | | | | (_| | (_) |"
Write-Host "|____// |\__,_|_| |_|\__, |\___/ "
Write-Host "    |__/             |___/       "
Write-Host " ____        _ _                 _       _       "
Write-Host "| __ )  ___ (_) | ___ _ __ _ __ | | __ _| |_ ___ "
Write-Host "|  _ \ / _ \| | |/ _ \ '__| '_ \| |/ _` | __/ _ \"
Write-Host "| |_) | (_) | | |  __/ |  | |_) | | (_| | ||  __/"
Write-Host "|____/ \___/|_|_|\___|_|  | .__/|_|\__,_|\__\___|"
Write-Host "                          |_|                    "

# Ask user if they want to create the .env file
$createEnv = Read-Host "Do you want to create a new .env file from .env_example? (y/n)"
if ($createEnv -eq "y") {
    $exampleEnvPath = "app\.env_example"
    $envPath = "app\.env"
    
    if (Test-Path $exampleEnvPath) {
        Copy-Item -Path $exampleEnvPath -Destination $envPath
        Write-Host "File '$envPath' created with the following content:"
        Write-Host "----------------------------------------------------"
        Get-Content -Path $envPath
        Write-Host "----------------------------------------------------"
    } else {
        Write-Host "Example environment file '$exampleEnvPath' does not exist. Skipping creation of '$envPath'."
    }
} else {
    Write-Host "Skipping .env file creation."
}

Write-Host "Downloading package information from all configured sources"
Write-Host "----------------------------------------------------"
if (Is-CommandAvailable "choco") {
    choco upgrade chocolatey
    Write-Host "Package information Downloaded 😎"
} else {
    Write-Host "Chocolatey is not installed. Please install Chocolatey to manage packages."
    exit 1
}
Write-Host "----------------------------------------------------"

Write-Host "Set executable permission to the rest generator"
Write-Host "----------------------------------------------------"
# On Windows, you usually don't need to set executable permissions, but if you do, use:
# icacls app\rest_generator.sh /grant Everyone:F
Write-Host "Executable permission set to rest generator 😎"
Write-Host "----------------------------------------------------"

Write-Host "Installing JQ"
Write-Host "----------------------------------------------------"
if (-not (Is-CommandAvailable "jq")) {
    choco install jq -y
} else {
    Write-Host "JQ is already installed. Skipping installation."
}
Write-Host "----------------------------------------------------"
Write-Host "JQ Installed 😎"
Write-Host "----------------------------------------------------"

Write-Host "Installing Postgres Database"
Write-Host "----------------------------------------------------"

# Ask user if they want to create a new PostgreSQL user and database
$createDb = Read-Host "Do you want to create a new PostgreSQL user and database? (y/n)"
if ($createDb -eq "y") {
    if (-not (Is-PackageInstalled "postgresql")) {
        choco install postgresql -y
    } else {
        Write-Host "PostgreSQL is already installed. Skipping installation."
    }

    Write-Host "Creating a new PostgreSQL user and database"
    Write-Host "----------------------------------------------------"
    
    $newUser = Read-Host "Enter the new user name"
    $newPassword = Read-Host -AsSecureString "Enter the password for the new user" | ConvertFrom-SecureString -AsPlainText
    $newDb = Read-Host "Enter the database name"

    Write-Host "New User: $newUser"
    Write-Host "New Database: $newDb"

    Write-Host "Creating a new PostgreSQL user..."
    & "C:\Program Files\PostgreSQL\13\bin\psql.exe" -c "CREATE USER $newUser WITH PASSWORD '$newPassword';"
    
    Write-Host "Creating a new database and assigning privileges to the new user..."
    & "C:\Program Files\PostgreSQL\13\bin\psql.exe" -c "CREATE DATABASE $newDb;"
    & "C:\Program Files\PostgreSQL\13\bin\psql.exe" -c "GRANT ALL PRIVILEGES ON DATABASE $newDb TO $newUser;"
    & "C:\Program Files\PostgreSQL\13\bin\psql.exe" -d $newDb -c "ALTER SCHEMA public OWNER TO $newUser;"

    Write-Host "PostgreSQL configuration for remote access is typically managed via `pgAdmin` or other tools."
    Write-Host "Please ensure that remote access is configured as needed."
    
    Write-Host "----------------------------------------------------"
    Write-Host "Postgres User and Database Created 😎"
} else {
    Write-Host "Skipping PostgreSQL user and database creation."
}
Write-Host "----------------------------------------------------"

Write-Host "Checking Python 3.11"
Write-Host "----------------------------------------------------"
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "3\.11") {
    Write-Host "Python 3.11 is already installed."
} else {
    Write-Host "Python 3.11 is not installed. Installing..."
    choco install python --version=3.11.0 -y
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "3\.11") {
        Write-Host "Python 3.11 installed successfully."
    } else {
        Write-Host "Failed to install Python 3.11. Please check the installation manually."
        exit 1
    }
}
Write-Host "----------------------------------------------------"
Write-Host "Python 3.11 check and installation completed 😎"
Write-Host "----------------------------------------------------"

Write-Host "Installing Python 3.11 venv module"
Write-Host "----------------------------------------------------"
# On Windows, the venv module comes pre-installed with Python, so no need for this step
Write-Host "Python 3.11 venv module Installed 😎"
Write-Host "----------------------------------------------------"

Write-Host "Creating Virtual Environment"
Write-Host "----------------------------------------------------"
if (-not (Test-Path "env")) {
    python -m venv env
} else {
    Write-Host "Virtual Environment already exists. Skipping creation."
}
Write-Host "----------------------------------------------------"
Write-Host "Virtual env Created 😎"
Write-Host "----------------------------------------------------"

Write-Host "Activating Virtual Environment"
Write-Host "----------------------------------------------------"
& env\Scripts\Activate
Write-Host "----------------------------------------------------"
Write-Host "Virtual env activated 😎"
Write-Host "----------------------------------------------------"

Write-Host "Installing python level dependencies"
Write-Host "----------------------------------------------------"
pip install -r app\requirements.txt
Write-Host "----------------------------------------------------"
Write-Host "python level dependencies Installed 😎"
Write-Host "----------------------------------------------------"

Write-Host "Install pre-commit hooks"
Write-Host "----------------------------------------------------"
pre-commit install 
pre-commit install --hook-type commit-msg
Write-Host "----------------------------------------------------"
Write-Host "Pre-commit hooks installed 😎"
Write-Host "----------------------------------------------------"

Write-Host "Deactivating virtual Environment"
Write-Host "----------------------------------------------------"
deactivate
Write-Host "----------------------------------------------------"
Write-Host "Virtual Environment Deactivated 😎"
Write-Host "----------------------------------------------------"

Write-Host "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"
if ($createEnv -eq "y") {
    Write-Host "░░░░░░  Now U have to provide the exact value in $envPath And run the below files. ░░░░░░"
}
Write-Host "░░░░░░  apply_migrations.sh - Applying the migrations                                   ░░░░░░"
Write-Host "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"
