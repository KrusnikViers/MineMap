#!/usr/bin/python3
import json
import subprocess

import net_util


# Download local installation for latest released texture pack.
def _update_client():
  manifest = net_util.get(
    'https://launchermeta.mojang.com/mc/game/version_manifest.json')
  version_id = manifest['latest']['release']

  version_path = '/versions/{0}/{0}.jar'.format(version_id)
  net_util.download(
    'https://s3.amazonaws.com/Minecraft.Download' + version_path,
    '/bin/client.jar')


# Request authentication information to access Minecraft API.
def _request_authentication():
  with open('/bin/configuration.json') as configuration_file:
      configuration = json.load(configuration_file)
  request_data = {
    'username': configuration['email'],
    'password': configuration['password'],
    'agent': {'name': 'Minecraft', 'version': 1},
    'clientToken': 'MineMapServer'
  }
  response = net_util.post('https://authserver.mojang.com/authenticate',
                           json.dumps(request_data))
  return {
    'token': response['accessToken'],
    'name': response['selectedProfile']['name'],
    'id': response['selectedProfile']['id'],
    'version': configuration['version']
  }


# Download latest world backup from Realms server.
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


# Unpack world data and process it with overviewer.
def _publish_map():
  def execute_sequence(commands):
    for command in commands:
      if subprocess.run(command, shell=True).returncode != 0:
        break

  execute_sequence([
      'mkdir -p /rendering/world',
      'mkdir -p /rendering/new_version',
      'gunzip -c /rendering/world.tar.gz > /rendering/world.tar',
      'tar -xvf /rendering/world.tar -C /rendering/',
      'overviewer.py --config=/bin/config.py',
      'rm -rf /public/*',
      'mv /rendering/new_version/* /public/',
      'rm -rf ./rendering/*'
    ])


def rebuild_map():
  _update_client()
  auth_data = _request_authentication()
  _download_world_to_file(auth_data)
  _publish_map()


if __name__ == "__main__":
    rebuild_map()
