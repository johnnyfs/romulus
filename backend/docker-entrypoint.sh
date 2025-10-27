#!/bin/bash
set -e

echo "Waiting for postgres..."
while ! pg_isready -h postgres -U romulus; do
  sleep 1
done

echo "PostgreSQL started"

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
