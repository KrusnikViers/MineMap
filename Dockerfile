FROM python:3.5

# Install Overviewer.
RUN apt-get install -y wget gnupg &&\
    echo "deb http://overviewer.org/debian ./" >> /etc/apt/sources.list &&\
    wget -O - https://overviewer.org/debian/overviewer.gpg.asc | apt-key add - &&\
    apt-get update &&\
    apt-get install -y minecraft-overviewer

# Move nginx and python resources into container.
COPY resources /minemap/resources

# Install nginx. |daemon off| prevents nginx from daemonizing.
RUN apt-get install -y nginx                                     &&\
    rm /etc/nginx/sites-enabled/default                          &&\
    cp /minemap/resources/minemap.nginx /etc/nginx/sites-enabled &&\
    echo 'daemon off;' >> /etc/nginx/nginx.conf

# Install base python dependencies.
RUN pip3 install --no-cache-dir --upgrade -r /minemap/resources/requirements.txt

# Clean up after installation.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Move, set and validate main scripts
COPY scripts /minemap/scripts
COPY configuration.json /minemap/scripts
RUN python /minemap/scripts/validate_config.py
CMD ["/minemap/scripts/entry.sh"]
