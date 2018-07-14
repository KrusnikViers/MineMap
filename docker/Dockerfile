FROM python:3.5

RUN apt-get update

# Install base dependencies.
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir --upgrade -r /tmp/requirements.txt

# Install Overviewer.
RUN apt-get install -y wget gnupg &&\
    echo "deb http://overviewer.org/debian ./" >> /etc/apt/sources.list &&\
    wget -O - https://overviewer.org/debian/overviewer.gpg.asc | apt-key add - &&\
    apt-get update &&\
    apt-get install -y minecraft-overviewer

# Install nginx. |daemon off| prevents nginx from daemonizing.
RUN apt-get install -y nginx &&\
    rm /etc/nginx/sites-enabled/default &&\
    echo 'daemon off;' >> /etc/nginx/nginx.conf
COPY config.nginx /etc/nginx/sites-enabled

# Clean after installation.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Move main container infrastructure scripts.
RUN mkdir /bin
RUN mkdir /public
RUN mkdir /rendering

COPY configuration.json /bin
COPY impl /bin

COPY entry.sh /bin
CMD ["/bin/entry.sh"]
