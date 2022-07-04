#!/bin/sh

if [ "$DEBUG" = 1 ]  # because postgres only runs in docker in DEBUG mode
then
echo "Waiting for db.."
python manage.py check --database default > /dev/null 2> /dev/null
until [ $? -eq 0 ];
do
  sleep 2
  python manage.py check --database default > /dev/null 2> /dev/null
done
echo "Connected."
fi

python manage.py migrate
python manage.py collectstatic --no-input

exec "$@"