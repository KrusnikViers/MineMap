#!/usr/bin/python3
import json
import os
import requests
import shutil


def _request_authentication():
  with open('/configuration.json') as configuration_file:
      configuration = json.load(configuration_file)

  request_data = {
    'username': configuration['email'],
    'password': configuration['password'],
    'agent': {'name': 'Minecraft', 'version': 1},
    'clientToken': 'MineMap'
  }
  response = requests.post('https://authserver.mojang.com/authenticate', json.dumps(request_data)).text
  response = json.loads(response)

  return {
    'token': response['accessToken'],
    'name': response['selectedProfile']['name'],
    'id': response['selectedProfile']['id'],
    'version': configuration['version']
  }


def _download_world_to_file(auth_data):
  cookies = {
    'sid': "token:{}:{}".format(auth_data['token'], auth_data['id']),
    'user': auth_data['name'],
    'version': auth_data['version']
  }

  def _get_request(url):
    request = requests.get(url, cookies=cookies)
    print('Response:\n' + request.text)
    return json.loads(request.text)

  # Request first world id
  world_id = _get_request('https://pc.realms.minecraft.net/worlds')['servers'][0]['id']

  # Request download link
  download_link = _get_request(
    'https://pc.realms.minecraft.net/worlds/{}/slot/1/download'.format(world_id))['downloadLink']

  # Download world to file
  request = requests.get(download_link, stream=True)
  file_name = '/rendering/world.tar.gz'
  if request.status_code == 200:
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'wb') as file:
      request.raw.decode_content = True
      shutil.copyfileobj(request.raw, file)


# def _publish_map():
#   os.system('cd /impl/rendering')
#   os.system('gunzip rendering/world.tar.gz')
#   os.system('tar xvf world.tar')
#   os.system('overviewer.py --config=/impl/config.py')


def rebuild_map():
  auth_data = _request_authentication()
  _download_world_to_file(auth_data)
  # _publish_map()


if __name__ == "__main__":
    rebuild_map()
