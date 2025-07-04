#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
python manage.py check --database default

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity=2

# List static files to verify collection
echo "Static files collected to:"
ls -la staticfiles/

# Check if admin static files exist
if [ -d "staticfiles/admin" ]; then
    echo "Admin static files found"
else
    echo "Warning: Admin static files not found"
fi

# Start the application
echo "Starting application..."
exec gunicorn mimi_ecom.wsgi:application --bind 0.0.0.0:$PORT --workers 3