#!/bin/bash

python /bin/entry.py

nginx -t
# Disable nginx during development process
# nginx
