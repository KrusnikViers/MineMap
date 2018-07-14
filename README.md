# MineMap
Map builder for official minecraft realms

Fill configuration file and put it into `docker` folder inside the repository root. Remove |.example| from file name. This file will be ignored by git.

To build docker image, set repository root as working directory and do:
`docker build --no-cache --force-rm -t minemap-image ./docker/`

To run built container:
`docker run -d --name minemap-instance --net="host" minemap-image --restart always
