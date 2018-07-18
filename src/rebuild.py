#!/usr/bin/python3
import crontab
import datetime
import json
import os
import requests
import shutil
import subprocess
import time


def http_get(url: str, cookies=None):
    return json.loads(requests.get(url, cookies=cookies).text)


def http_post(url: str, request_data):
    return json.loads(requests.post(url, json.dumps(request_data)).text)


def download_to_file(url: str, location: str):
    os.makedirs(os.path.dirname(location), exist_ok=True)
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(location, 'wb') as file:
            request.raw.decode_content = True
            shutil.copyfileobj(request.raw, file)


def get_latest_backup():
    # Download local installation for latest released texture pack.
    client_version_id = http_get('https://launchermeta.mojang.com/mc/game/version_manifest.json')['latest']['release']
    download_to_file('https://s3.amazonaws.com/Minecraft.Download/versions/{0}/{0}.jar'.format(client_version_id),
                     '/build/client.jar')

    # Request authentication to access API.
    with open('/src/configuration.json') as configuration_file:
        configuration = json.load(configuration_file)
    auth_request_body = {
        'username': configuration['email'],
        'password': configuration['password'],
        'agent': {'name': 'Minecraft', 'version': 1},
        'clientToken': 'MineMapServer',
    }
    auth_response = http_post('https://authserver.mojang.com/authenticate', auth_request_body)

    # Download latest world backup from Realms server.
    cookies = {
        'sid': 'token:{}:{}'.format(auth_response['accessToken'], auth_response['selectedProfile']['id']),
        'user': auth_response['selectedProfile']['name'],
        'version': configuration['version'],
    }
    realms_url = 'https://pc.realms.minecraft.net/worlds'
    first_world_id = http_get(realms_url, cookies)['servers'][0]['id']
    download_link = http_get(realms_url + '/{}/slot/1/download'.format(first_world_id), cookies)['downloadLink']
    download_to_file(download_link, 'build/world.tar.gz')


def render_backup():
    def execute_sequence(commands):
        for command in commands:
            if subprocess.run(command, shell=True).returncode != 0:
                raise ValueError('Subprocess command failed!')

    execute_sequence([
        'mkdir -p /build',
        'mkdir -p /public',
        'gunzip -c /build/world.tar.gz > /build/world.tar',
        'tar -xvf /build/world.tar -C /build/',
        'overviewer.py --config=/src/overviewer_config.py',
        'rm -rf /public/*',
        'mv /build/public/* /public/',
        'rm -rf /build/*'
    ])


def finish_update(start_downloading_time, start_rendering_time, previous_data):
    # Shrink old records.
    max_old_records = 49
    previous_data['renders'] = previous_data['renders'][:max_old_records]

    # Insert new record in the beginning.
    downloading_time = datetime.timedelta(seconds=(start_rendering_time - start_downloading_time))
    rendering_time = datetime.timedelta(seconds=(time.time() - start_rendering_time))
    current_time = datetime.datetime.now()
    new_record = json.loads(
        '{"downloading":"' + str(downloading_time) + '",'
        '"rendering":"' + str(rendering_time) + '",'
        '"at":"' + str(current_time) + '"}')
    previous_data['renders'] = [new_record] + previous_data['renders']

    # Check, that next updates are automated.
    cron = crontab.CronTab(user=True)
    if not len(list(cron.find_comment('minemap'))):
        # Rounded hours, spent on previous rendering + 1
        hours_count = ((time.time() - start_downloading_time) + 1800) // 3600 + 1
        job = cron.new(command='python /src/rebuild.py', comment='minemap')
        job.hour.every(hours_count)
        previous_data['update_period_hours'] = str(hours_count)
        cron.write()

    # Dump data
    with open("/public/version_data.txt", "w") as version_file:
        json.dump(previous_data, version_file)


def update_render():
    previous_version_data = json.loads('{"renders":[]}')
    if os.path.exists('/public/version_data.txt'):
        with open('/public/version_data.txt') as version_file:
            previous_version_data = json.load(version_file)

    start_downloading_time = time.time()
    get_latest_backup()

    start_rendering_time = time.time()
    render_backup()

    finish_update(start_downloading_time, start_rendering_time, previous_version_data)


update_render()
