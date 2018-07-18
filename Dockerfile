FROM python:3.5

# Install Overviewer.
RUN apt-get install -y wget gnupg                                              &&\
    echo "deb http://overviewer.org/debian ./" >> /etc/apt/sources.list        &&\
    wget -O - https://overviewer.org/debian/overviewer.gpg.asc | apt-key add - &&\
    apt-get update &&\
    apt-get install -y minecraft-overviewer

# Install nginx. |daemon off| prevents nginx from daemonizing.
RUN apt-get install -y nginx                      &&\
    rm /etc/nginx/sites-enabled/default           &&\
    cp /src/server.nginx /etc/nginx/sites-enabled &&\
    echo 'daemon off;' >> /etc/nginx/nginx.conf

# Install base python dependencies.
RUN pip3 install --no-cache-dir --upgrade -r /src/requirements.txt

# Install cron to automate updates.
RUN apt-get install -y cron

# Clean up after installation.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Move sources into container.
RUN mkdir -p /public /build
COPY configuration.json /src
COPY src /src

# Move, set and validate main scripts
CMD ["/src/entry.sh"]

