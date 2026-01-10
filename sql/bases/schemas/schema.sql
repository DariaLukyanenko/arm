drop schema if exists ${POSTGRES_SCHEMA} cascade;

create schema ${POSTGRES_SCHEMA};

alter database ${POSTGRES_DB} set search_path to ${POSTGRES_SCHEMA}, public;
