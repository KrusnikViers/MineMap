#!/usr/bin/python3
import crontab
import datetime
import json
import os
import requests
import shutil
import subprocess
import time
import sys


# Load previous updates history
previous_updates = None
if os.path.exists('/public/version_data.txt'):
    with open('/public/version_data.txt') as version_file:
        previous_updates = json.load(version_file)['history']

# Start time measurement.
rebuild_timestamp = datetime.datetime.now()
start_time = time.time()


def finish(error_string = None):
    time_estimation_hours = 2
    time_spent = time.time() - start_time
    if not error_string:
        time_estimation_hours += (time_spent + 1800) // 3600

    # Update cron job, if necessary
    cron = crontab.CronTab(user=True)
    existing_jobs = list(cron.find_comment('minemap'))
    job = existing_jobs[0] if len(existing_jobs) else cron.new(command='python /src/rebuild.py', comment='minemap')
    job.hour.every(time_estimation_hours)
    cron.write()

    # Fill version_data.txt
    current_record = {'timestamp': str(rebuild_timestamp), 'estimation': str(time_estimation_hours)}
    if error_string:
        current_record['error'] = error_string
    else:
        current_record['build_time'] = str(datetime.timedelta(time_spent))
    history_to_write = [current_record]
    if previous_updates:
        history_to_write += previous_updates[:99]
    with open("/public/version_data.txt", "w") as output_file:
        json.dump(history_to_write, output_file, indent='  ')
    sys.exit(1 if error_string else 0)


def download_to_file(url: str, location: str):
    os.makedirs(os.path.dirname(location), exist_ok=True)
    download_request = requests.get(url, stream=True)
    if download_request.status_code == 200:
        with open(location, 'wb') as output_file:
            download_request.raw.decode_content = True
            shutil.copyfileobj(download_request.raw, output_file)
    else:
        finish('Downloading failed from ' + url)


def try_json_loads(string: str):
    try:
        return json.loads(string)
    except json.decoder.JSONDecodeError:
        return ''


def execute_sequence(commands):
    for command in commands:
        if subprocess.run(command, shell=True).returncode != 0:
            finish('Command failed: ' + command)


# Load client of the latest release version
request = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
client_versions = try_json_loads(request.text)
if not client_versions or 'latest' not in client_versions or 'release' not in client_versions['latest']:
    finish('Bad client versions response: ' + request.text)
client_version = client_versions['latest']['release']
download_to_file('https://s3.amazonaws.com/Minecraft.Download/versions/{0}/{0}.jar'.format(client_version),
                 '/build/client.jar')

# Request authentication to access API.
with open('/configuration.json') as configuration_file:
    configuration = json.load(configuration_file)
    request_body = {
        'username': configuration['email'],
        'password': configuration['password'],
        'agent': {'name': 'Minecraft', 'version': 1},
        'clientToken': 'MineMapServer',
    }
    request = requests.post('https://authserver.mojang.com/authenticate', json.dumps(request_body))
    auth_data = try_json_loads(request.text)
    if not auth_data or 'accessToken' not in auth_data or 'selectedProfile' not in auth_data:
        finish('Bad auth response: ' + request.text)
    cookies = {
        'sid': 'token:{}:{}'.format(auth_data['accessToken'], auth_data['selectedProfile']['id']),
        'user': auth_data['selectedProfile']['name'],
        'version': client_version,
    }

# Request latest server id.
request = requests.get('https://pc.realms.minecraft.net/worlds', cookies=cookies)
worlds_list = try_json_loads(request.text)
if not worlds_list or 'servers' not in worlds_list or len(worlds_list['servers']) == 0:
    finish('Bad worlds list response: ' + request.text)
first_world_id = worlds_list['servers'][0]['id']

# Try to download latest backup.
request = requests.get('https://pc.realms.minecraft.net/worlds/{}/slot/1/download'.format(first_world_id),
                       cookies=cookies)
backup_information = try_json_loads(request.text)
if not backup_information or 'downloadLink' not in backup_information:
    finish('Bad request for backup: ' + request.text)
download_link = backup_information['downloadLink']
download_to_file(download_link, '/build/world.tar.gz')

execute_sequence([
    'gunzip -c /build/world.tar.gz > /build/world.tar',
    'tar -xvf /build/world.tar -C /build/',
    'overviewer.py --config=/src/config.py',
    'overviewer.py --config=/src/config.py --genpoi --skip-players'
    'rm -rf /public/*',
    'mv /build/out/* /public/',
    'rm -rf /build/*'
])

finish()
