#!/usr/bin/python3
import requests
import os

def get(url: str, cookies=None):
  request = requests.get(url, cookies=cookies)
  print('GET request to {}:\n{}'.format(url, request.text))
  return json.loads(request.text)

def post(url: str, data):
  request = requests.post(url, data)
  print('POST request to {}:\n{}'.format(url, request.text))
  return json.loads(request.text)

def download(url: str, location: str):
  request = requests.get(download_link, stream=True)
  if request.status_code == 200:
    os.makedirs(os.path.dirname(location), exist_ok=True)
    print('Download from {} to {}'.format(url, os.path.dirname(location)))
    with open(location, 'wb') as file:
      request.raw.decode_content = True
      shutil.copyfileobj(request.raw, file)
