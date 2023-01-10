#!/bin/sh

if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for Mysql..."

    while ! nc -z $MYSQL_DATABASE_HOST $MYSQL_DATABASE_PORT; do
      sleep 0.1
    done
fi

# python manage.py makemigrations
python manage.py migrate --no-input
python manage.py loaddata user/fixtures/superuser.json --app user.user
python manage.py loaddata scanner/fixtures/tool.json --app scanner.tool

exec "$@"