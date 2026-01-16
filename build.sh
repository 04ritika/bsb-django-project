#!/usr/bin/env bash
# Exit immediately if any command fails
set -e

# Install all dependencies from requirements.txt
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
