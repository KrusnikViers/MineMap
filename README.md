# MineMap
Online self-updating map for official minecraft realms.

[![Docker Build Status](https://img.shields.io/docker/build/viers/minemap.svg)](https://hub.docker.com/r/viers/minemap/)
[![Docker Pulls](https://img.shields.io/docker/pulls/viers/minemap.svg)](https://hub.docker.com/r/viers/minemap/)
[![MicroBadger Size](https://images.microbadger.com/badges/image/viers/minemap.svg)](https://hub.docker.com/r/viers/minemap/)

### Running
Fill the configuration file (same as configuration.json.example). This file should be mounted during the `run` command.
The map data is building in the `/public` directory inside a docker image, so it is recommended to mount this directory
from the host OS as well, to use map data outside the image and recreate image without losing the rendered map.

Configuration file parameters:
* `email`: Email for Mojang account of realm holder.
* `password`: Password from Mojang account of realm holder.
* `name`: Realm name.
* `update_period`: Minimum update period, in hours.

Default docker run command: `docker run -d -v [path/to/host/public]:/public -v [path/to/configuration.json]:/configuration.json --name minemap --restart always -p 80:80 --cpu-shares 512 viers/minemap`,
where:

* `-d` - Detach after launch. To see logs, use `docker logs --follow minemap-instance`.
* `-v` - Mount file or directory into the container.
* `--name` - Container name.
* `--restart` - Restarting policy. 
* `-p` - Port mapping.
* `--cpu-shares 512` - reduce CPU priority of the container, so that map rebuild process would not block other containers on a server (default value of the parameter is 1024).
* `--memory=1200m` - restrict RAM usage of the container (to 1200M in example)

### Custom rendering configuration
Image provides default configuration for rendering. To tweak it, you could copy default configuration
[src/default_render_config.py], make all neccessary changes and mount the file during the container launch with
parameter `-v [path/to/custom/configuration]:/render_config.py`

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
