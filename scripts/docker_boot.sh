#! /bin/sh
if [ ! "${PORT}" ]
then
  export PORT=5000
fi
flask deploy
flask create-admin
flask forge
exec gunicorn -b 0.0.0.0:5000 --access-logfile - --error-logfile - wsgi:app
