#!/bin/sh

set -e

echo "Waiting for PostgreSQL to be ready..."

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec "$@"