#!/usr/bin/python3
import crontab
import json
import os

import refresh

# Update map for the first time.
refresh.rebuild_map()

# Automate next updates.
with open('/bin/configuration.json') as configuration_file:
  configuration = json.load(configuration_file)
  user_cron  = crontab.CronTab(user=True)
  job = cron.new(command='/usr/bin/python3 /impl/refresh.py')
  job.hour.every(int(configuration['update_period_hours']))
