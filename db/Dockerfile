FROM postgres:latest
RUN mkdir -p /archive && chmod 777 /archive
COPY init.sql /docker-entrypoint-initdb.d/
