#!/bin/sh

if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for Mysql..."

    while ! nc -z $MYSQL_DATABASE_HOST $MYSQL_DATABASE_PORT; do
      sleep 0.1
    done
fi

# python manage.py makemigrations
python manage.py migrate
python manage.py loaddata scanner/fixtures/superuser.json --app scanner.user
python manage.py loaddata scanner/fixtures/tool.json --app scanner.tool

exec "$@"