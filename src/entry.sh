#!/bin/bash

python /src/rebuild.py

nginx -t
nginx
