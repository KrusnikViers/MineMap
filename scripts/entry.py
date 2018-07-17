#!/usr/bin/python3
import crontab

import rebuild

# Automate next updates.
cron = crontab.CronTab()
if not cron.find_comment('minemap'):
  rebuild.update_render()
  job = cron.new(command='/usr/bin/python3 /scripts/rebuild.py', comment='minemap')
  job.hour.every(8)
  cron.write()
