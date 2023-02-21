#!/bin/bash
NAME="nauvus" # Name of the application
DJANGODIR=/home/projects/nauvus-backend/ # Django project directory
SOCKFILE=/home/projects/nauvus-backend/run/gunicorn.sock # we will communicate using this unix socket
VIRTUAL_ENV=/home/projects/nauvus-backend/venv # Virtual env directory
NUM_WORKERS=3 # how many worker processes should Gunicorn spawn (2 * num cores)
DJANGO_SETTINGS_MODULE=config.settings.production # which settings file should Django use
DJANGO_WSGI_MODULE=config.wsgi # WSGI module name
LOG_LEVEL=error
TIMEOUT=300

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
. ${VIRTUAL_ENV}/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

echo yes | python manage.py collectstatic --noinput
# python manage.py seed
# ./manage migrate

python manage.py compress
# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ${VIRTUAL_ENV}/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --timeout $TIMEOUT \
  -b 0.0.0.0:8000 \
  --bind=unix:$SOCKFILE \
  --log-level=$LOG_LEVEL \
  --log-file=/home/projects/nauvus-backend/logs/nauvus_gunicorn_error.log
