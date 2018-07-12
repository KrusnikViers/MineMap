#!/usr/bin/python3
import crontab
import json
import os

from refresh import rebuild_map

rebuild_map()

# user_cron  = crontab.CronTab(user=True)
# job = cron.new(command='/usr/bin/python /impl/refresh.py')
# job.minutes.every(configuration['update_period_minutes'])
