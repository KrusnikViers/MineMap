import json

with open('/minemap/scripts/configuration.json') as configuration_file:
  configuration = json.load(configuration_file)
  if 'email' not in configuration or \
     'password' not in configuration or \
     'version' not in configuration:
     raise ValueError('Configuration file malformed! Check example file fields.')
