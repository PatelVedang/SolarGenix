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
##### To Run server in detached mode( Means here run server in background)
#

    docker-compose up -d
    
##### Run below command to build and run server with single command:
#
    docker-compose up --build
    
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

# Run BETA server with live database
##### All the steps are same as running local database, just change was use -f flag to provide docker-compose.yml file rather than docker-compose.yml, because if i'm using docker-compose up at that time, it will use docker-compose.yml file in background. 
##### For example "docker-compose -f docker-compose.beta.yml build" to build the project for BETA enviorment.

#
#
# Steps to add ssh key in Azure VM instance
### Step 1
##### Connect with VM using ssh command
### Step 2
##### Append ssh key in "~/.ssh/authorized_keys" file

# Run Live server without docker
### Step 1 (Get latest code)
##### Clone the repo: https://isaix.visualstudio.com/CyberApp/_git/CyberApp
### Step 2(Make virtual environment)
```
python3 -m venv env
```
### Step 3(Activate virtual environment)
##### For Windows
#
```
cd env/Scripts
activate
cd ..
cd ..
```
##### For Linux
#
```
. env/bin/activate
```
### Step 4(Install system level dependencies)
#### For Linux
##### Install nmap
#
```
sudo apt-get update
sudo apt-get install nmap
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
### Step 5(Install requirements.txt)
##### We have to run below commands, when we want to restart server with new python dependencies.
#
```
cd ~/CyberApp/app/
pip install -r requirements.txt
```
##### Note: Make sure you have activate the virtual enviorment before running the above command
### Step 6(Apply latest migrations & fixtures)
##### We have to run below command, when we have new database migrations changes.
#
```
. ~/CyberApp/apply_migrations.sh
```
### Step 7(Run server with worker)
##### Run below command to start, restart and stop the server.
#
```
. ~/CyberApp/start-server.sh
```