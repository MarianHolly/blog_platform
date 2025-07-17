#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install Python dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser automatically if environment variables are provided
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
from accounts.models import Profile
import os

username = os.getenv('SUPERUSER_USERNAME', 'admin')
email = os.getenv('SUPERUSER_EMAIL', 'admin@blogplatform.sk')
password = os.getenv('SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Platform',
        last_name='Administrator'
    )
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={
            'role': 'admin',
            'biography': 'Správca platformy zodpovedný za moderovanie obsahu a správu používateľov.'
        }
    )
    print(f'Superuser created: {username}')
else:
    print(f'Superuser {username} already exists')
"

echo "Build completed successfully!"
echo "Blog Platform is ready to launch!"