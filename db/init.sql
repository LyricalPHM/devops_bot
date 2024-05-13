CREATE DATABASE my_database1;

CREATE TABLE email (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE phone (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL
);

SELECT pg_create_physical_replication_slot('replication_slot');
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';
CREATE TABLE hba ( lines text ); 
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf'; 
INSERT INTO hba (lines) VALUES ('host replication all 0.0.0.0/0 md5'); 
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf'; 
SELECT pg_reload_conf();
