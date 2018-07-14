#!/usr/bin/python3
import json
import os
import requests
import shutil

import net_util


def _request_authentication():
  with open('/configuration.json') as configuration_file:
      configuration = json.load(configuration_file)
  request_data = {
    'username': configuration['email'],
    'password': configuration['password'],
    'agent': {'name': 'Minecraft', 'version': 1},
    'clientToken': 'MineMap'
  }
  response = net_util.post('https://authserver.mojang.com/authenticate',
                           json.dumps(request_data))
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
  # Request first world id
  world_id = net_util.get(
    'https://pc.realms.minecraft.net/worlds', cookies)['servers'][0]['id']
  # Request download link
  download_link = net_util.get(
    'https://pc.realms.minecraft.net/worlds/{}/slot/1/download'.format(world_id),
    cookies)['downloadLink']
  # Download world to file
  net_util.download(download_link, '/rendering/world.tar.gz')


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
