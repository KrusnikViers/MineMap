#!/usr/bin/python3
import datetime
import json
import subprocess
import time

import net_util


client_manifest_url = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
client_download_url = 'https://s3.amazonaws.com/Minecraft.Download/versions/{0}/{0}.jar'
auth_server_url = 'https://authserver.mojang.com/authenticate'
realms_server_url = 'https://pc.realms.minecraft.net/worlds'


# Download local installation for latest released texture pack.
def update_client():
  manifest = net_util.get(client_manifest_url)
  version_id = manifest['latest']['release']
  net_util.download(client_download_url.format(version_id),
                    '/minemap/rendering/client.jar')


# Request authentication information to access Minecraft API.
def request_authentication():
  with open('/minemap/scripts/configuration.json') as configuration_file:
      configuration = json.load(configuration_file)
  request_data = {
    'username': configuration['email'],
    'password': configuration['password'],
    'agent': {'name': 'Minecraft', 'version': 1},
    'clientToken': 'MineMapServer'
  }
  response = net_util.post(auth_server_url, json.dumps(request_data))
  return {
    'sid': 'token:{}:{}'.format(response['accessToken'], response['selectedProfile']['id'])
    'user': response['selectedProfile']['name'],
    'version': configuration['version']
  }


# Download latest world backup from Realms server.
def download_world_to_file(auth_data):
  # Request first world id
  world_id = net_util.get(realms_server_url, auth_data)['servers'][0]['id']
  # Request download link
  download_link = net_util.get(
    realms_server_url + '/{}/slot/1/download'.format(world_id), auth_data)['downloadLink']
  # Download world to file
  net_util.download(download_link, '/minemap/rendering/world.tar.gz')


# Unpack world data and process it with overviewer.
def publish_map(start_time):
  def execute_sequence(commands):
    for command in commands:
      if subprocess.run(command, shell=True).returncode != 0:
        break

  execute_sequence([
      'mkdir -p /minemap/rendering/world',
      'mkdir -p /minemap/rendering/public',
      'mkdir -p /minemap/public',
      'gunzip -c /minemap/rendering/world.tar.gz > /minemap/rendering/world.tar',
      'tar -xvf /minemap/rendering/world.tar -C /minemap/rendering/',
      'overviewer.py --config=/minemap/scripts/overviewer_config.py',
      'rm -rf /minemap/public/*',
      'mv /minemap/rendering/public/* /minemap/public/',
      'rm -rf /minemap/rendering/*'
    ])
  with open("/minemap/public/last_version.txt", "w") as version_file:
    version_file.write('Last update was at: {}\nRendering time:{}\n'.format(
      datetime.datetime.now().isoformat(),
      str(datetime.timedelta(seconds=int(time.time() - start_time)))))


def rebuild_map():
  start_time = time.time()
  update_client()
  auth_data = request_authentication()
  download_world_to_file(auth_data)
  publish_map(start_time)


if __name__ == "__main__":
    rebuild_map()
