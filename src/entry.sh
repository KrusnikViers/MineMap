#!/bin/bash

if [ -s "/configuration.json" ]
then
    cd /src
    python -u ./main.py
else
   echo "Configuration file is empty!"
fi
