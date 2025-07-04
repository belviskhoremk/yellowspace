#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
python manage.py check --database default

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start the application
echo "Starting application..."
exec gunicorn mimi_ecom.wsgi:application --bind 0.0.0.0:$PORT --workers 3