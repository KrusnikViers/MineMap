#!/usr/bin/python3
import datetime
import json
import os
import subprocess
import time

from rebuild import rebuild

nginx_process = subprocess.Popen(['nginx'])
with open('/configuration.json') as configuration_file:
    configuration = json.load(configuration_file)

# Main process exists in endless cycle, until container is stopped from the outside.
while True:
    start_time_full = datetime.datetime.now()
    start_time = time.time()

    subprocess.run('rm -rf /public/log.txt', shell=True)

    result = rebuild(configuration['email'], configuration['password'], configuration['realm_name'])
    subprocess.run('rm -rf /build/*', shell=True)

    previous_updates = []
    if os.path.exists('/public/updates.txt'):
        with open('/public/updates.txt') as version_file:
            previous_updates = json.load(version_file)['history']
    current_record = {'timestamp': str(start_time_full), 'result': str(result)}
    with open('/public/updates.txt', 'w') as version_file:
        json.dump({'history': previous_updates[:99] + [current_record]}, version_file, indent='  ')

    end_time = time.time()
    time_left = int(configuration['update_period']) * 3600 - (end_time - start_time)
    if time_left > 0:
        time.sleep(time_left)
