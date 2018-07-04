#!/usr/bin/python
import json

with open('/configuration.json') as configuration_file:
    configuration = json.load(configuration_file)

print('Email: {}, Password: {}'.format(configuration['email'], configuration['Password']))
