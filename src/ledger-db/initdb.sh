#!/bin/sh
# create schema and populate transactions table.
# these should be idempotent:
psql -f /docker-entrypoint-initdb.d/0_init_tables.sql -h $POSTGRES_HOST -p $POSTGRES_PORT --dbname $POSTGRES_DB --username $POSTGRES_USER
/docker-entrypoint-initdb.d/1_create_transactions.sh
