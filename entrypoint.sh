#!/bin/sh
set -e

# Wait for the database to be ready
until pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing"

python manage.py migrate
python manage.py collectstatic --no-input

exec gunicorn core.wsgi:application --bind 0.0.0.0:8000
