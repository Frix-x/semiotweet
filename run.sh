#!/bin/bash

#echo STARTINGD RUN.SH FOR STARTING DJANGO SERVER PORT IS $PORT
#
#echo ENVIRONMENT VAIRABLES IN RUN.SH
#printenv


#Change this values for django superuser
#USER="admin"
#MAIL="carlosyells@yahoo.com"
#PASS="admin"

if [ -z "$VCAP_APP_PORT" ];
  then SERVER_PORT=5000;
  else SERVER_PORT="$VCAP_APP_PORT";
fi

echo [$0] port is------------------- $SERVER_PORT
python manage.py makemigrations
python manage.py migrate

echo [$0] Starting Django Server...
#python manage.py runserver 0.0.0.0:$SERVER_PORT --noreload

NAME="Semiotweet_Server"                                # Name of the application
NUM_WORKERS=3                                           # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE="semiotweet.settings"            # which settings file should Django use
DJANGO_WSGI_MODULE="semiotweet.wsgi"                    # WSGI module name
TIMEOUT=120                                             # Worker Timeout
KEEPALIVE=75                                            # Keep Alive Timer

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --keep-alive $KEEPALIVE \
  --timeout $TIMEOUT
