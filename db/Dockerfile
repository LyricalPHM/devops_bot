FROM postgres:latest
RUN mkdir -p /archive && chmod 777 /archive
RUN mkdir -p /var/log/
RUN chown postgres:postgres /var/log/
COPY init.sql /docker-entrypoint-initdb.d/
