#!/bin/bash


echo "Make migrations cataloga"
python manage.py makemigrations catalog

echo "Make migrations reviews"
python manage.py makemigrations reviews

echo "Make migrations users"
python manage.py makemigrations users

echo "Apply database migrations"
python manage.py migrate

echo "Collect static files"
python manage.py collectstatic --no-input

echo "Installing Gunicorn"
gunicorn api_yamdb.wsgi:application --bind 0:8000