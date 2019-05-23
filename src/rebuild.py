#!/usr/bin/python3
import json
import os
import shutil
import subprocess

import requests


class ExecutionResult:
    def __init__(self, data=None, error_string=''):
        self.data = data
        self.error_string = error_string

    def is_ok(self) -> bool:
        return not self.error_string

    def __str__(self) -> str:
        return ('ERROR: {}'.format(self.error_string) if self.error_string else 'No error') + \
               (', DATA: {}'.format(self.data) if self.data else ', no data')


def _download_to_file(url: str, location: str) -> ExecutionResult:
    os.makedirs(os.path.dirname(location), exist_ok=True)
    download_request = requests.get(url, stream=True)
    if download_request.status_code == 200:
        with open(location, 'wb') as output_file:
            download_request.raw.decode_content = True
            shutil.copyfileobj(download_request.raw, output_file)
            return ExecutionResult()
    return ExecutionResult(error_string='Download to {} failed from {}'.format(location, url))


def _request_json(url: str, is_get_request=True, body=None, cookies=None) -> ExecutionResult:
    if is_get_request:
        current_request = requests.get(url, cookies=cookies)
    else:
        current_request = requests.post(url, body, cookies=cookies)

    try:
        return ExecutionResult(data=json.loads(current_request.text))
    except json.decoder.JSONDecodeError:
        return ExecutionResult(error_string='Bad response: {}'.format(current_request.text))


def _execute_sequence(commands) -> ExecutionResult:
    for command in commands:
        if subprocess.run(command, shell=True).returncode != 0:
            return ExecutionResult(error_string='Command failed: {}'.format(command))
    return ExecutionResult()


def rebuild(email, password, realm_name) -> ExecutionResult:
    # Client version and manifest
    get_version_result = _request_json('https://launchermeta.mojang.com/mc/game/version_manifest.json')
    if not get_version_result.is_ok() or 'versions' not in get_version_result.data:
        return ExecutionResult(error_string='Bad client versions list: {}'.format(get_version_result))
    latest_version = get_version_result.data['versions'][0]
    manifest_url = latest_version['url']
    version_id = latest_version['id']

    # Client storage server
    manifest_result = _request_json(manifest_url)
    if not manifest_result.is_ok() or 'downloads' not in manifest_result.data:
        return ExecutionResult(error_string='Bad client manifest: {}'.format(manifest_result))

    # Get the client itself
    client_download_result = _download_to_file(manifest_result.data['downloads']['client']['url'], '/build/client.jar')
    if not client_download_result.is_ok():
        return client_download_result

    # Request authentication to the Realms API
    request_body = {
        'username': email,
        'password': password,
        'agent': {'name': 'Minecraft', 'version': 1},
        'clientToken': 'MinemapServer'
    }
    auth_result = _request_json('https://authserver.mojang.com/authenticate',
                                is_get_request=False, body=json.dumps(request_body))
    if not auth_result.is_ok() or 'accessToken' not in auth_result.data or 'selectedProfile' not in auth_result.data:
        return ExecutionResult(error_string='Bad auth response: {}'.format(auth_result))

    # Request necessary server id
    cookies = {
        'sid': 'token:{}:{}'.format(auth_result.data['accessToken'], auth_result.data['selectedProfile']['id']),
        'user': auth_result.data['selectedProfile']['name'],
        'version': version_id,
    }
    realms_result = _request_json('https://pc.realms.minecraft.net/worlds', cookies=cookies)
    world_id = None
    if not realms_result.is_ok() or 'servers' not in realms_result.data or len(realms_result.data['servers']) == 0:
        return ExecutionResult(error_string='Bad realms list response: {}'.format(realms_result))

    # Look for the world id among the realms
    for server in realms_result.data['servers']:
        if server['name'] == realm_name:
            world_id = server['id']
            break
    if not world_id:
        return ExecutionResult(error_string='Realm {} not found in {}'.format(realm_name, realms_result.data))

    # Download the latest backup
    backup_metadata_result = _request_json('https://pc.realms.minecraft.net/worlds/{}/slot/1/download'.format(world_id),
                                           cookies=cookies)
    if not backup_metadata_result.is_ok() or 'downloadLink' not in backup_metadata_result.data:
        return ExecutionResult(error_string='Bad backup metadata: {}'.format(backup_metadata_result))

    download_backup_result = _download_to_file(backup_metadata_result.data['downloadLink'], '/build/world.tar.gz')
    if not download_backup_result.is_ok():
        return download_backup_result

    return _execute_sequence([
        'gunzip -c /build/world.tar.gz > /build/world.tar',
        'tar -xvf /build/world.tar -C /build/',
        'overviewer.py --config=/src/config.py >> /public/log.txt',
        'overviewer.py --config=/src/config.py --genpoi --skip-players >> /public/log.txt'
    ])
