#!/usr/bin/env bash
set -o errexit

echo "Starting build process..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify gunicorn
echo "Checking gunicorn..."
python -c "import gunicorn; print(f'Gunicorn version: {gunicorn.__version__}')"

python manage.py collectstatic --no-input
python manage.py migrate
echo "Build completed!"