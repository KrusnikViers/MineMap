#!/usr/bin/python3
import json
import os
import requests
import shutil

def get(url: str, cookies=None):
  request = requests.get(url, cookies=cookies)
  return json.loads(request.text)

def post(url: str, data):
  request = requests.post(url, data)
  return json.loads(request.text)

def download(url: str, location: str):
  os.makedirs(os.path.dirname(location), exist_ok=True)
  request = requests.get(url, stream=True)
  if request.status_code == 200:
    with open(location, 'wb') as file:
      request.raw.decode_content = True
      shutil.copyfileobj(request.raw, file)
