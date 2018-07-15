#!/usr/bin/python3
import crontab

import refresh

# Update map for the first time.
refresh.rebuild_map()

# Automate next updates.
user_cron  = crontab.CronTab()
job = cron.new(command='/usr/bin/python3 /bin/refresh.py')
job.hour.on(0)
