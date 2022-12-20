# Run Live server
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
    
    
