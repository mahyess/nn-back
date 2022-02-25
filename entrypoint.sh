#!/bin/sh

if [ "$DEBUG" = 1 ]  # because postgres only runs in docker in DEBUG mode
then
echo "before checking db"
until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Waiting for db..."
  sleep 1
done
fi

python manage.py migrate
python manage.py collectstatic --no-input

exec "$@"