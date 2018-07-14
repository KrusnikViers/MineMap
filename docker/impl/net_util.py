#!/usr/bin/python3
import json
import os
import requests
import shutil

def get(url: str, cookies=None):
  request = requests.get(url, cookies=cookies)
  print('GET request to {}: {}'.format(url, request.status_code))
  return json.loads(request.text)

def post(url: str, data):
  request = requests.post(url, data)
  print('POST request to {}: {}'.format(url, request.status_code))
  return json.loads(request.text)

def download(url: str, location: str):
  request = requests.get(url, stream=True)
  if request.status_code == 200:
    os.makedirs(os.path.dirname(location), exist_ok=True)
    print('Download from {} to {}'.format(url, os.path.dirname(location)))
    with open(location, 'wb') as file:
      request.raw.decode_content = True
      shutil.copyfileobj(request.raw, file)
