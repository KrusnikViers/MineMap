#!/usr/bin/python3
import json
import requests

with open('/configuration.json') as configuration_file:
    configuration = json.load(configuration_file)

# Trying to get access token from auth server:
auth_request_data = {
  'username': configuration['username'],
  'password': configuration['password'],
  'agent': {'name': 'Minecraft', 'version': 1},
  'clientToken': 'MineMap'
}
auth_request_url = 'https://authserver.mojang.com/authenticate'
auth_request = requests.post(auth_request_url, json.dumps(auth_request_data))

auth_response = json.loads(auth_request.text)
print(auth_response)
