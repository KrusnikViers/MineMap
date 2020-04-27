FROM ubuntu:18.04

EXPOSE 80

# Build overviewer from sources on the particular commit.
RUN apt-get update                                                      && \
    apt-get install -y                                                     \
        nginx                                                              \
        python3                                                            \
        build-essential                                                    \
        python3-pip                                                        \
        python3-pillow                                                     \
        python3-numpy                                                      \
        git                                                             && \
    pip3 install --no-cache-dir --upgrade requests==2.23                && \
    mkdir /overviewer                                                   && \
    cd /overviewer                                                      && \
    git clone https://github.com/overviewer/Minecraft-Overviewer.git .  && \
    git reset --hard bdca0b92509f542ed69f051554f7db91f20bddd9           && \
    python3 setup.py build                                              && \
    apt-get purge -y                                                       \
        build-essential                                                    \
        python3-pip                                                        \
        git                                                             && \
    apt-get autoremove -y                                               && \
    apt-get clean                                                       && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy Minemap source files
COPY src /src

# Create working directories and set up nginx
RUN rm /etc/nginx/sites-enabled/default           && \
    echo 'daemon off;' >> /etc/nginx/nginx.conf   && \
    mv /src/server.nginx /etc/nginx/sites-enabled && \
    mkdir -p /public /build

CMD ["/src/entry.sh"]
