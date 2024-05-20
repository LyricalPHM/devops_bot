FROM postgres:15.6

RUN apt-get update
RUN apt-get install gettext-base

COPY ./init.sql /docker-entrypoint-initdb.d/init.sql.raw
RUN mkdir -p /etc/postgresql/
RUN mkdir -p /archive/
RUN chown postgres:postgres /archive/

ENTRYPOINT [ "bash", "-c", "\
mkdir -p /var/log/ && \
chown postgres:postgres /var/log/ && \
envsubst < /docker-entrypoint-initdb.d/init.sql.raw > /docker-entrypoint-initdb.d/init.sql \n\
echo \"listen_addresses = '*'\" > /etc/postgresql/postgresql.conf && \
echo \"port = ${DB_PORT}\" >> /etc/postgresql/postgresql.conf && \
echo \"log_destination = 'stderr'\" >> /etc/postgresql/postgresql.conf && \
echo \"logging_collector = on\" >> /etc/postgresql/postgresql.conf && \
echo \"log_directory = '/var/log/'\" >> /etc/postgresql/postgresql.conf && \
echo \"log_filename = 'repl.log'\" >> /etc/postgresql/postgresql.conf && \
echo \"archive_mode = on\" >> /etc/postgresql/postgresql.conf && \
echo \"archive_command = 'cp %p /archive/%f'\" >> /etc/postgresql/postgresql.conf && \
echo \"max_wal_senders = 10\" >> /etc/postgresql/postgresql.conf && \
echo \"wal_level = replica\" >> /etc/postgresql/postgresql.conf && \
echo \"wal_log_hints = on\" >> /etc/postgresql/postgresql.conf && \
echo \"log_replication_commands = on\" >> /etc/postgresql/postgresql.conf && \
echo \"host all all 0.0.0.0/0 password\" >> /etc/postgresql/pg_hba.conf && \
echo \"host replication ${DB_REPL_USER} 0.0.0.0/0 trust\" >> /etc/postgresql/pg_hba.conf && \
echo \"local   all             ${POSTGRES_USER}                                   trust\" >> /etc/postgresql/pg_hba.conf && \
docker-entrypoint.sh \"$@\""]

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf", "-c", "hba_file=/etc/postgresql/pg_hba.conf" ]
