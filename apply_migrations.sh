#!/bin/sh

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


printf "░░░░░░  Running the migrations ░░░░░░ \n\n\n"
. env/bin/activate
python app/manage.py migrate --no-input
# printf "░░░░░░  Running the fixtures ░░░░░░ \n\n\n"
# python app/manage.py loaddata app/scanner/fixtures/tool.json --app scanner.tool
deactivate

if [ $? = 0 ] 
then
	printf " \n\n Job Done 😎 \n\n"
else
	printf " \n\n Oops 😟, Something Went Wrong \n\n"
fi