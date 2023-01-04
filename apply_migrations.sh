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


printf "░░░░░░  Running the migrations ░░░░░░ \n\n\n"
python manage.py migrate --no-input
printf "░░░░░░  Running the fixtures ░░░░░░ \n\n\n"
python manage.py loaddata scanner/fixtures/superuser.json --app scanner.user
python manage.py loaddata scanner/fixtures/tool.json --app scanner.tool
printf " \n\n Job Done 😎 \n\n"