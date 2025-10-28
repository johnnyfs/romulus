#!/bin/bash
set -e

# Extract host and port from DATABASE_URL
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):\([0-9]*\).*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):\([0-9]*\).*/\2/p')

echo "Waiting for postgres at $DB_HOST:$DB_PORT..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U romulus; do
  sleep 1
done

echo "PostgreSQL started"

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
