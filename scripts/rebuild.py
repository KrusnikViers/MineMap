#!/usr/bin/python3
import datetime
import json
import os
import requests
import shutil
import subprocess
import time

public_dir = '/public'
build_dir = '/build'

def _get_latest_backup():
  auth_server_url = 'https://authserver.mojang.com/authenticate'
  client_download_url = 'https://s3.amazonaws.com/Minecraft.Download/versions/{0}/{0}.jar'
  manifest_url = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
  realms_wolrds_url = 'https://pc.realms.minecraft.net/worlds/'

  def http_get(url: str, cookies=None):
    return json.loads(requests.get(url, cookies=cookies).text)

  def http_post(url: str, request_data):
    return json.loads(requests.post(url, json.dumps(request_data)))

  def download(url: str, location: str):
    os.makedirs(os.path.dirname(location), exist_ok=True)
    request = requests.get(url, stream=True)
    if request.status_code == 200:
      with open(location, 'wb') as file:
        request.raw.decode_content = True
        shutil.copyfileobj(request.raw, file)

  # Download local installation for latest released texture pack.
  client_version_id = http_get(client_manifest_url)['latest']['release']
  download(client_download_url.format(client_version_id), build_dir + '/client.jar')

  # Request authentication information to access Minecraft API.
  with open('/resources/configuration.json') as configuration_file:
    configuration = json.load(configuration_file)
  auth_request_data = {
    'username': configuration['email'],
    'password': configuration['password'],
    'agent': {'name': 'Minecraft', 'version': 1},
    'clientToken': 'MineMapServer'
  }
  auth_response = http_post(auth_server_url, auth_request_data)
  cookies = {
    'sid': 'token:{}:{}'.format(auth_response['accessToken'], auth_response['selectedProfile']['id'])
    'user': auth_response['selectedProfile']['name'],
    'version': configuration['version']
  }

  # Download latest world backup from Realms server.
  first_world_id = http_get(realms_wolrds_url, cookies)['servers'][0]['id']
  download_link = http_get(realms_wolrds_url + first_world_id + '/slot/1/download', cookies)['downloadLink']
  download(download_link, build_dir + '/world.tar.gz')


# Unpack world data and process it with overviewer.
def _render_backup():
  def execute_sequence(commands):
    for command in commands:
      if subprocess.run(command, shell=True).returncode != 0:
        raise ValueError('Subprocess command failed!')

  execute_sequence([
      'mkdir -p {}'.format(build_dir),
      'mkdir -p {}'.format(public_dir),
      'gunzip -c {0}/world.tar.gz > {0}/world.tar'.format(build_dir),
      'tar -xvf {0}/world.tar -C {0}/'.format(build_dir),
      'overviewer.py --config=/resources/config.py',
      'rm -rf {}/*'.format(public_dir),
      'mv {}/public/* {}/'.format(build_dir, public_dir),
      'rm -rf {}/*'.format(build_dir)
    ])

def update_render():
  start_time = time.time()
  _get_latest_backup()
  _render_backup()
  with open(public_dir + "/last_version.txt", "w") as version_file:
    version_file.write('Last update was at: {}\nRendering time:{}\n'.format(datetime.datetime.now().isoformat(), str(datetime.timedelta(seconds=int(time.time() - start_time)))))

if __name__ == "__main__":
    update_render()
