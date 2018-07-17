#!/usr/bin/python3
import crontab

import refresh

# Automate next updates.
cron = crontab.CronTab()
if not cron.find_comment('minemap'):
  # Update map for the first time.
  refresh.rebuild_map()

  job = cron.new(command='/usr/bin/python3 /minemap/scripts/refresh.py',
                 comment='minemap')
  job.hour.every(8)
  cron.write()
