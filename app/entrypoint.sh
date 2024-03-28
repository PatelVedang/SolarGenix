#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $MYSQL_DATABASE_HOST $MYSQL_DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# python manage.py makemigrations
python3 manage.py migrate --no-input
python3 manage.py loaddata user/fixtures/role.json --app user.role
python3 manage.py loaddata scanner/fixtures/subscription.json --app scanner.subscription
python3 manage.py loaddata user/fixtures/superuser.json --app user.user
python3 manage.py loaddata scanner/fixtures/tool.json --app scanner.tool

exec "$@"