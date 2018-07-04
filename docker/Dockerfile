FROM python:3.6

# Add overviewer repo, install overviewer and nginx
RUN apt-add-repository 'deb http://overviewer.org/debian ./'                  && \
    wget -O - http://overviewer.org/debian/overviewer.gpg.asc | apt-key add - && \
    apt-get update                                                            && \
    apt-get install -y nginx minecraft-overviewer                             && \
    apt-get clean                                                             && \
    echo 'daemon off;' >> /etc/nginx/nginx.conf

# Copy python requirements and install them
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir --upgrade -r /tmp/requirements.txt

# Copy common configuration
COPY ../configuration.json /

# Copy nginx configuration
COPY minemap.nginx /etc/nginx/sites-enabled/

# Copy implementation scripts
COPY impl /

# Copy and set entrypoint script
COPY minemap_entry.sh /
CMD ["/minemap_entry.sh"]
