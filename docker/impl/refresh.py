#!/usr/bin/python3
import json
import requests

def request_authentication():
    with open('/configuration.json') as configuration_file:
        configuration = json.load(configuration_file)

    # Trying to get access token from auth server:
    auth_request_data = {
      'username': configuration['email'],
      'password': configuration['password'],
      'agent': {'name': 'Minecraft', 'version': 1},
      'clientToken': 'MineMap'
    }
    auth_request_url = 'https://authserver.mojang.com/authenticate'
    auth_request = requests.post(auth_request_url, json.dumps(auth_request_data))
    auth_response = json.loads(auth_request.text)
    # Temporary
    print(auth_response)

def rebuild_map():
    auth_data = request_authentication()

if __name__ == "__main__":
    rebuild_map()
