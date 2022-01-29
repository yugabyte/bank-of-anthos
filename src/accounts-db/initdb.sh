#!/bin/sh
# create schema and populate accounts table.
# these should be idempotent:
psql -f /docker-entrypoint-initdb.d/0-accounts-schema.sql -h $POSTGRES_HOST -p $POSTGRES_PORT --dbname $POSTGRES_DB --username $POSTGRES_USER
/docker-entrypoint-initdb.d/1-load-testdata.sh
