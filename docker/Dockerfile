FROM debian:stretch

RUN apt-get update

# Install base dependencies
COPY requirements.txt /tmp/
RUN apt-get install -y python3.5 python3-pip && \
    pip3 install --upgrade pip               && \
    pip3 install --no-cache-dir --upgrade -r /tmp/requirements.txt

# Install Overviewer
RUN apt-get install -y wget gnupg                                              && \
    echo "deb http://overviewer.org/debian ./" >> /etc/apt/sources.list        && \
    wget -O - https://overviewer.org/debian/overviewer.gpg.asc | apt-key add - && \
    apt-get update                                                             && \
    apt-get install -y minecraft-overviewer

# Install nginx.
# 'daemon off' prevents nginx from daemonizing, thus first called process
# remains alive, helping Docker to watch it.
RUN apt-get install -y nginx                    && \
    echo 'daemon off;' >> /etc/nginx/nginx.conf
COPY config.nginx /etc/nginx/sites-enabled/

# Clean everything after installation
RUN apt-get clean                                 && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Move main container infrastructure scripts
COPY configuration.json /
COPY impl/* /impl/
COPY entry.sh /
CMD ["/entry.sh"]
