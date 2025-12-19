#!/bin/sh
set -e

python manage.py migrate
python manage.py collectstatic --noinput

exec gunicorn clubelmeta.wsgi:application --bind 0.0.0.0:8080
