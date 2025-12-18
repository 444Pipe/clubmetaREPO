release: python manage.py migrate && python manage.py createsu && python manage.py collectstatic --noinput
web: gunicorn clubelmeta.wsgi:application --log-file -
