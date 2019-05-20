#!/bin/bash

if [ -s "/configuration.json" ]
then
    python -u /src/rebuild.py
    service cron start
    nginx -t
    nginx
else
   echo "Configuration file is empty!"
fi
