#!/usr/bin/env bash
# Exit on error
set -o errexit


# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser
python create_superuser.py

echo "Superuser created with email: codexweb.sj@gmail.com and password: 123"