#!/bin/bash

if [ -s "/configuration.json" ]
then
    cd /src
    python ./main.py
else
   echo "Configuration file is empty!"
fi
