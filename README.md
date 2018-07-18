# MineMap
Map builder for official minecraft realms

Fill configuration file and put it into `docker` folder inside the repository root. Remove |.example| from file name. This file will be ignored by git.

To build docker image, set repository root as working directory and do:
`docker build --no-cache --force-rm -t minemap-image .`

To run built container:
`docker run -d --name minemap-instance --net="host" --sig-proxy=false minemap-image --restart always`
