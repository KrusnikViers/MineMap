#!/usr/bin/python3
import crontab
import json
import os

with open('/configuration.json') as configuration_file:
    configuration = json.load(configuration_file)
print(configuration)

os.system("/impl/refresh.py")

# user_cron  = crontab.CronTab(user=True)
# job = cron.new(command='/usr/bin/python /impl/refresh.py')
# job.minutes.every(configuration['update_period_minutes'])
