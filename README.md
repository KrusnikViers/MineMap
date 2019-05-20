# MineMap
Online map for official minecraft realms.

[![Docker Build Status](https://img.shields.io/docker/build/viers/minemap.svg)](https://hub.docker.com/r/viers/minemap/)
[![Docker Pulls](https://img.shields.io/docker/pulls/viers/minemap.svg)](https://hub.docker.com/r/viers/minemap/)
[![MicroBadger Size](https://images.microbadger.com/badges/image/viers/minemap.svg)](https://hub.docker.com/r/viers/minemap/)

### Running
Fill the configuration file (same as configuration.json.example). This file should be mounted during the `run` command.

Default run command: `docker run -d -v [path/to/configuration.json]:/configuration.json --name minemap-instance --restart always -p 80:80 viers/minemap`,
where:

* `-d` - Detach after launch. To see logs, use `docker logs --follow minemap-instance`.
* `-v` - Pass file into container. Replace `[path/to/configuration.json]` with absolute path to filled configuration file.
* `--name` - Container name.
* `--restart` - Restarting policy. 
* `-p` - Port mapping.

### Building
Default build command: `docker build --no-cache --force-rm -t minemap-image .`

### How it works
This image includes nginx server and minecraft-overviewer installation.

Map building process:
1. Download latest client .jar, to get newest textures.
2. Authenticate with credentials from configuration.
3. Access the first server in user realms list.
4. Download latest backup for this server.
5. Unpack backup and run overviewer on it.

Map is rebuilding over time, where period is a previous build time + 2 hours. Additional logs are in the `version_data.txt` file, which is also available on a server via direct link. Repeating is implemented as a cron tasks, while nginx is the main image process.
