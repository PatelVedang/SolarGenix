# Run Local server
### Step 1
##### Clone the repo: https://isaix.visualstudio.com/CyberApp/_git/CyberApp
### Step 2
```
cd ~/CyberAPP
```
### Step 3

##### Run below command to install all the dependencies and to create the container(we create a new build to perform new migrations of project):
#
    docker-compose build

##### Run below command to run the server:
#
    docker-compose up
##### or
#
#
##### To Run server in detached mode( Means here run server in background)
#

    docker-compose up -d
    
##### Run below command to build and run server with single command:
#
    docker-compose up --build
#
#
#
# Some docker command which we are frequently use
##### Run below command to get IP Address of database container(Only for local use)
#
    docker inspect cyber_db | grep IPAddress
    
##### Run below command to stop runnung server without loosing volume(data) 
##### Note: We only use down command without -v flag when server running in detached mode
#
    docker-compose down
##### Run below command to stop runnung server and make volume empty
#
    docker-compose down -v
##### Run below command to build and run server with single command:
#
    docker-compose up --build
#
#
#
# Add a user to the VM instance's MySQL database and grant all user access to the database. 
### Step 1
##### Connect with mysql using root user using below command
#
    sudo mysql -u root -p
### Step 2
##### To create a database and select a database, run the command below in the MySQL shell.
#
    CREATE DATABASE IF NOT EXISTS <db_name>;
    USE <db_name>;
##### Run the following command to create a user for MySQL. Here we use '%' to access user from any IP.
#
    CREATE USER '<username>'@'%' IDENTIFIED BY '<password>';
##### By executing below command for specific database, it will grant all privileges to declared username in command.
#
    GRANT ALL PRIVILEGES ON <db_name>.* TO '<username>'@'%' WITH GRANT OPTION;
##### Note: Make sure to run below command to apply changes which make in MySQL.
#
    FLUSH PRIVILEGES;
#
#
#
# Run BETA server with live database
##### All the steps are same as running local database, just change was use -f flag to provide docker-compose.yml file rather than docker-compose.yml, because if i'm using docker-compose up at that time, it will use docker-compose.yml file in background. 
##### For example "docker-compose -f docker-compose.beta.yml build" to build the project for BETA enviorment.
#
#
#
# Steps to add ssh key in Azure VM instance
### Step 1
##### Connect with VM using ssh command
### Step 2
##### Append new ssh key in "~/.ssh/authorized_keys" file
#
#
#
# Steps to run unit testing
### Linux
```
cd CyberApp
bash unit_test.sh
```
### Windows
```
cd CyberApp
unit_test.bat
```
##### Note: All test_<current_database_name> database rights must be granted to the current database username. For instance, if the database name is db_dev then the username must have all the rights of the test_db_dev database. If you want add to privileges then use this "GRANT ALL PRIVILEGES" command of section "Add a user to the VM instance’s MySQL database and grant all user access to the database". 
#
#
#
# Run Live server without docker
### Step 1 (Get latest code)
##### Clone the repo: https://isaix.visualstudio.com/CyberApp/_git/CyberApp
### Step 2(Set .env in proj folder)
```
cd ~/CyberApp/app/proj
nano .env
```
##### Note: Use .env variables(content) from .env_example file
### Step 3(Install system level dependencies)
#### For Linux
##### Install nmap
#
```
sudo apt-get update
sudo apt-get install nmap
```
##### Install wkhtmltopdf
#
```
sudo apt-get install wkhtmltopdf
```
##### Install MySQL development headers 
#
```
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
```
##### Install rabbitMQ
#
```
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
sudo systemctl status rabbitmq-server
```
##### Install PM2 with NVM
#
```
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
source ~/.bashrc
nvm install node
npm install pm2 -g
```
#### For Windows
##### Install nmap using below link
#
```
https://nmap.org/dist/nmap-7.92-setup.exe
```
##### Install wkhtmltopdf using below link
###### Note: Must set wkhtmltopdf path in environment variable
#
```
https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe
```
##### Install rabbitMQ server using below 
#
```
https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.11.6/rabbitmq-server-3.11.6.exe
```
##### Install PM2 and Concurrently packages with NVM, After downloading and installing nvm setup you have to run other two commands in new terminal 
#
```
https://github.com/coreybutler/nvm-windows/releases/download/1.1.10/nvm-setup.exe
```
```
nvm install node
npm i -g concurrently pm2
```
### Step 4(Make virtual environment)
```
cd CyberApp
python3 -m venv env
```
### Step 5(Activate virtual environment)
##### For Windows
#
```
cd CyberApp
env\Scripts\activate
```
##### For Linux
#
```
cd CyberApp
. env/bin/activate
```
### Step 6(Install requirements.txt)
##### We have to run below commands, when we want to restart server with new python dependencies.
#
```
pip install -r app/requirements.txt
```
##### Note: Make sure you have activate the virtual enviorment before running the above command
### Step 7(Apply latest migrations & fixtures)
##### We have to run below command, when we have new database migrations changes.
##### For Linux
#
```
bash apply_migrations.sh
```
##### For Windows
#
```
apply_migrations.bat
```
### Step 8(Run server with worker)
##### Run below command to start, stop, restart and delete a server process with worker.
##### For Linux
#
```
bash server.sh
```
##### For Windows
#
```
server.bat
```
### Step 9(View server logs)
```
pm2 logs
```