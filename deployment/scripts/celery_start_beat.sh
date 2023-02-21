#!/usr/bin/env bash

echo "Celery start"

PROJECTDIR=/home/projects/nauvus-backend/
VIRTUAL_ENV=/home/projects/nauvus-backend/venv # Virtual env directory
DJANGO_SETTINGS_MODULE=config.settings.production # which settings file should Django use

cd $PROJECTDIR
. ${VIRTUAL_ENV}/bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$PROJECTDIR:$PYTHONPATH

exec celery -A config.celery_app beat -l INFO
