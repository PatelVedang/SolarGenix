#!/bin/sh

# python manage.py makemigrations
python manage.py migrate
python manage.py loaddata scanner/fixtures/superuser.json --app scanner.user
python manage.py loaddata scanner/fixtures/tool.json --app scanner.tool

exec "$@"