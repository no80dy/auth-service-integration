#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z $PG_DB_HOST $PG_DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

exec "$@"