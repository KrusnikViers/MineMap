#!/usr/bin/python3
import datetime
import json
import os
import subprocess
import time

from rebuild import RebuildException, OverviewerMapBuilder
from settings import CONFIGURATION_FILE_PATH, LOG_FILE_PATH, HISTORY_FILE_PATH

try:
    with open(CONFIGURATION_FILE_PATH) as configuration_file:
        configuration = json.load(configuration_file)
        period = int(configuration['update_period']) * 3600
        map_builder = OverviewerMapBuilder(configuration)
except FileNotFoundError:
    print("Configuration file was not found. Please, check the documentation on how to mount the file.")
    exit(1)

web_server_process = subprocess.Popen(['nginx'])

def _print_history(rebuild_start_time, rebuild_end_time, rebuild_result):
    previous_history = []
    if os.path.exists(HISTORY_FILE_PATH):
        try:
            with open(HISTORY_FILE_PATH) as version_file:
                previous_history = json.load(version_file)['history']
        except json.decoder.JSONDecodeError:
            pass

    current_record = {'started_at': str(rebuild_start_time),
                      'duration': str(rebuild_end_time - rebuild_start_time),
                      'result': str(rebuild_result)}
    with open(HISTORY_FILE_PATH, 'w') as version_file:
        json.dump({'history': previous_history[:99] + [current_record]}, version_file, indent='  ')


# Main process exists in endless cycle, until container is stopped from the outside.

while True:
    print('Rebuild is in progress!')
    start_time = datetime.datetime.now()

    try:
        subprocess.run('rm -rf {}'.format(LOG_FILE_PATH), shell=True)
        map_builder.rebuild()
        current_rebuild_result = 'Finished without errors'
        print('Rebuild successfully finished')
    except RebuildException as exc:
        print('Error has occurred: {}'.format(str(exc)))
        current_rebuild_result = 'ERROR! {}'.format(str(exc))

    end_time = datetime.datetime.now()

    _print_history(start_time, end_time, current_rebuild_result)
    time_left = period - (end_time - start_time).seconds
    if time_left > 0:
        print('Sleeping until {}'.format(str(end_time + datetime.timedelta(seconds=time_left))))
        time.sleep(time_left)
