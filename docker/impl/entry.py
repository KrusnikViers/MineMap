#!/usr/bin/python3
import crontab
import json
import os

import net_util
import refresh

# Download local installation for texture pack.
manifest = net_util.get(
  'https://launchermeta.mojang.com/mc/game/version_manifest.json')
version_id = manifest['latest']['release']

version_path = '/{0}/{0}.jar'.format(version_id)
net_util.download(
  'https://s3.amazonaws.com/Minecraft.Download/versions' + version_path,
  '~/.minecraft/versions' + version_path)

# Update map for the first time.
refresh.rebuild_map()

# Automate next updates.
# TODO(Viers)
# user_cron  = crontab.CronTab(user=True)
# job = cron.new(command='/usr/bin/python /impl/refresh.py')
# job.minutes.every(configuration['update_period_minutes'])
