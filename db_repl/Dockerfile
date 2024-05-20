FROM postgres:15.6
RUN mkdir -p /etc/postgresql/ 
RUN chmod +r /var/lib/postgresql/data
RUN rm -rf /var/lib/postgresql/data/*

RUN echo "GRANT SELECT ON email TO ${DB_REPL_USER};" >> /docker-entrypoint-initdb.d/init.sql \
    && echo "GRANT SELECT ON phone TO ${DB_REPL_USER};" >> /docker-entrypoint-initdb.d/init.sql
