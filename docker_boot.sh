#! /bin/sh
flask deploy
flask create-admin
flask forge
flask translate compile
exec gunicorn -b :5000 --access-logfile - --error-logfile - wsgi:app
