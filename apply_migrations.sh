#!/bin/sh

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


printf "░░░░░░  Running the migrations ░░░░░░ \n\n\n"
. env/bin/activate
python app/manage.py migrate --no-input
printf "░░░░░░  Running the fixtures ░░░░░░ \n\n\n"
python app/manage.py loaddata app/user/fixtures/superuser.json --app user.user
python app/manage.py loaddata app/scanner/fixtures/tool.json --app scanner.tool
python manage.py loaddata app/scanner/fixtures/subscription.json --app scanner.subscription
deactivate

if [ $? = 0 ] 
then
	printf " \n\n Job Done 😎 \n\n"
else
	printf " \n\n Oops 😟, Something Went Wrong \n\n"
fi