#!/usr/bin/python3
import json
import os
import shutil
import subprocess
import time

import requests
from settings import MINECRAFT_CLIENT_PATH, WORLD_BACKUP_PATH, LOG_FILE_PATH, RENDER_CONFIGURATION_FILE_PATH


class RebuildException(Exception):
    pass


def _retry_on_timeout(lambda_f):
    timeout_minutes = 15
    while True:
        try:
            return lambda_f()
        except requests.exceptions.Timeout as e:
            print('Timeout is reached during network call; retrying in {} minutes...'.format(timeout_minutes))
            time.sleep(timeout_minutes * 60)


# Download file from |url| to |location|
def _download_to_file(url: str, location: str):
    os.makedirs(os.path.dirname(location), exist_ok=True)
    download_request = _retry_on_timeout(lambda: requests.get(url, stream=True, timeout=60))
    if download_request.status_code != 200:
        raise RebuildException('Download from {} to {} failed: {}'.format(url, location, str(download_request)))
    with open(location, 'wb') as output_file:
        download_request.raw.decode_content = True
        shutil.copyfileobj(download_request.raw, output_file)


# GET or POST request on specified url, expects JSON as an answer.
def _get_json(url: str, post_body=None, cookies=None):
    if post_body:
        current_request = _retry_on_timeout(lambda: requests.post(url, post_body, cookies=cookies, timeout=60))
    else:
        current_request = _retry_on_timeout(lambda: requests.get(url, cookies=cookies, timeout=60))

    try:
        return json.loads(current_request.text)
    except json.decoder.JSONDecodeError:
        raise RebuildException('Bad response from {}: {}'.format(url, current_request.text))


# Execute sequence of shell commands, stops and raises exception, if one of them returned non-zero result.
def _execute_sequence(commands):
    for command in commands:
        if subprocess.run(command, shell=True).returncode != 0:
            raise RebuildException('Shell command failed: {}'.format(command))


# Class for rebuilding a Minecraft map using the minecraft-overviewer. It is caching some data between rebuilds, so it
# is recommended to use the same instance for multiple map renderings.
class OverviewerMapBuilder:
    def __init__(self, configuration):
        self.email = configuration['email']
        self.password = configuration['password']
        self.realm_name = configuration['realm_name']

        self.current_client = None
        self.authorised_cookies = None

    @staticmethod
    def _get_latest_version_id_and_manifest() -> (str, str):
        version_data = _get_json('https://launchermeta.mojang.com/mc/game/version_manifest.json')
        if not 'versions' in version_data:
            raise RebuildException('Bad client versions list: {}'.format(version_data))
        latest_version = version_data['versions'][0]
        return latest_version['id'], latest_version['url']

    def _update_current_client(self, client_id, manifest_url):
        # Remove old client, if any.
        if os.path.exists(MINECRAFT_CLIENT_PATH):
            _execute_sequence(['rm -f {}'.format(MINECRAFT_CLIENT_PATH)])

        client_manifest = _get_json(manifest_url)
        if 'downloads' not in client_manifest:
            raise RebuildException('Bad client manifest: {}'.format(client_manifest))
        _download_to_file(client_manifest['downloads']['client']['url'], MINECRAFT_CLIENT_PATH)

        self.current_client = client_id

    def _update_authorised_cookies(self):
        request_body = {
            'username': self.email,
            'password': self.password,
            'agent': {'name': 'Minecraft', 'version': 1},
            'clientToken': 'MinemapServer'
        }
        auth_data = _get_json('https://authserver.mojang.com/authenticate', post_body=json.dumps(request_body))
        if 'accessToken' not in auth_data or 'selectedProfile' not in auth_data:
            raise RebuildException('Bad auth response: {}'.format(auth_data))

        self.authorised_cookies = {
            'sid': 'token:{}:{}'.format(auth_data['accessToken'], auth_data['selectedProfile']['id']),
            'user': auth_data['selectedProfile']['name'],
            'version': self.current_client,
        }

    def _get_world_id(self):
        realms_list = _get_json('https://pc.realms.minecraft.net/worlds', cookies=self.authorised_cookies)
        if 'servers' not in realms_list or len(realms_list['servers']) == 0:
            raise RebuildException('Bad realms list: {}'.format(realms_list))

        # Look for the world id among the realms
        for server in realms_list['servers']:
            if server['name'] == self.realm_name:
                return server['id']
        raise RebuildException('Realm \'{}\' was not found: {}'.format(self.realm_name, realms_list['servers']))

    def _get_world_download_link(self, world_id: str):
        try:
            backup_metadata = _get_json(
                'https://pc.realms.minecraft.net/worlds/{}/slot/1/download'.format(world_id),
                cookies=self.authorised_cookies)
        except RebuildException as exc:
            if 'Retry again later' in str(exc):
                print('Should retry again later, waiting 15s...')
                time.sleep(15)
                backup_metadata = _get_json(
                    'https://pc.realms.minecraft.net/worlds/{}/slot/1/download'.format(world_id),
                    cookies=self.authorised_cookies)
            else:
                raise exc

        if 'downloadLink' not in backup_metadata:
            raise RebuildException('Bad backup metadata: {}'.format(backup_metadata))
        return backup_metadata['downloadLink']

    @staticmethod
    def _prepare_world_backup(download_link: str):
        _download_to_file(download_link, WORLD_BACKUP_PATH)
        _execute_sequence([
            'gunzip -c /build/world.tar.gz > /build/world.tar',
            'tar -xvf /build/world.tar -C /build/'
        ])

    @staticmethod
    def _rebuild_map():
        _execute_sequence([
            '/overviewer/overviewer.py --config={0} >> {1}'.format(RENDER_CONFIGURATION_FILE_PATH, LOG_FILE_PATH),
            '/overviewer/overviewer.py --config={0} --genpoi >> {1}'.format(RENDER_CONFIGURATION_FILE_PATH,
                                                                            LOG_FILE_PATH),
            'rm -rf /build/world*'
        ])

    def rebuild(self):
        print('Requesting current client version...')
        current_client_version, manifest_url = self._get_latest_version_id_and_manifest()
        if self.current_client != current_client_version:
            print('Updating current client...')
            self._update_current_client(current_client_version, manifest_url)

        backup_link = None
        # Try to use previous token:
        if self.authorised_cookies:
            try:
                print('Requesting backup link with previous token...')
                backup_link = self._get_world_download_link(self._get_world_id())
            except RebuildException:
                pass
        if not backup_link:
            print('Updating token...')
            self._update_authorised_cookies()
            print('Requesting backup link...')
            backup_link = self._get_world_download_link(self._get_world_id())

        print('Downloading and unpacking the world...')
        self._prepare_world_backup(backup_link)
        print('Rendering...')
        self._rebuild_map()
