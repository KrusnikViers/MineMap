# MineMap
Map builder for official minecraft realms.

### Running
Fill the configuration file (same as configuration.json.example). This file should be mounted during the `run`

Container could be started with this command:
`docker run -d -v [path/to/configuration.json]:/configuration.json --name minemap-instance --restart always -p 80:80 minemap-image`

* `-d` - Detach after launch. To see logs, use `docker logs --follow minemap-instance`.
* `-v` - Pass file into container. Replace `[path/to/configuration.json]` with absolute path to filled configuration file.
* `--name` - Container name.
* `--restart` - Restarting policy. 
* `-p` - Port mapping.

### Building
`docker build --no-cache --force-rm -t minemap-image .`

### How it works
This image includes nginx server and minecraft-overviewer installation.

Map building process:
1. Download latest client .jar, to get newest textures.
2. Authenticate with credentials from configuration.
3. Access the first server in user realms list.
4. Download latest backup for this server.
5. Unpack backup and run overviewer on it.

Map building is repeating over time, period is previous build time + 2 hours. Additional logs are in `version_data.txt` file, which is also available on server via direct link.
