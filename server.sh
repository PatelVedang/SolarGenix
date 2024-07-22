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


printf "\n\n\nPlease select the option \n\n"
printf "Start : 1 \n"
printf "Restart : 2 \n"
printf "Stop : 3 \n"
printf "Delete : 4 \n\n"

echo -n "Enter the value :  "
read -r option

printf "You have entered : $option \n\n"




if [ $option == 1 ];
then
    # START
    printf "░░░░░░  Starting the app ░░░░░░ \n\n\n"
    . env/bin/activate
    cd app
    if [ $? -eq 1 ] 
    then
        printf " \n\n Oops 😟, Something Went Wrong \n\n"
    fi
    pm2 start "python manage.py runserver 0.0.0.0:8000" --name cyber_appliance --max-memory-restart "100M" --no-autorestart
    printf "░░░░░░  Starting the worker ░░░░░░ \n\n\n"
    pm2 start "celery -A proj worker --pool=prefork --concurrency=20 --loglevel=info" --name worker --max-memory-restart "800M"
    printf "░░░░░░  Starting the ZAP server ░░░░░░ \n\n\n"
    pm2 start zap.sh --name zap_server -- -daemon -port 8080 -host 127.0.0.1 -config api.disablekey=true
    cd ..
    deactivate
    printf " \n\n Job Done 😎 \n\n"
elif [ $option == 2 ];
then
    # RESTART
    printf "░░░░░░  Restarting the app ░░░░░░ \n\n\n"
    pm2 restart cyber_appliance
    printf "░░░░░░  Restarting the worker ░░░░░░ \n\n\n"
    pm2 restart worker
    printf "░░░░░░  Restarting the ZAP server ░░░░░░ \n\n\n"
    pm2 restart zap_server
    printf " \n\n Job Done 😎 \n\n"
elif [ $option == 3  ];
then
    # STOP
    printf "░░░░░░  Stopping the app ░░░░░░ \n\n\n"
    pm2 stop cyber_appliance
    printf "░░░░░░  Stopping the worker ░░░░░░ \n\n\n"
    pm2 stop worker
    printf "░░░░░░  Stopping the ZAP server ░░░░░░ \n\n\n"
    pm2 stop zap_server
    printf " \n\n Job Done 😎 \n\n"
elif [ $option == 4  ];
then
    # DELETE
    printf "░░░░░░  Deleting the app ░░░░░░ \n\n\n"
    pm2 delete cyber_appliance
    printf "░░░░░░  Deleting the worker ░░░░░░ \n\n\n"
    pm2 delete worker
    printf "░░░░░░  Deleting the ZAP server ░░░░░░ \n\n\n"
    pm2 delete zap_server
    printf " \n\n Job Done 😎 \n\n"
else
    printf "Wrong Choice!!!😂 Try Again!!😜 \n"
fi