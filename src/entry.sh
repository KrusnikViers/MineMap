#!/bin/bash

python /src/rebuild.py

service cron start

nginx -t
nginx
