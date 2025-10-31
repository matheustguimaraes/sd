#!/bin/bash

echo 'running database migrations'
python manage.py migrate

echo 'deploying backend server'
python manage.py runserver 0.0.0.0:8000

