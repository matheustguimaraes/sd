#!/bin/env bash

#psql -c 'create database alvee_re_staging'
#python3 manage.py collectstatic --noinput
#echo 'running database migrations'
python3 manage.py migrate --noinput
python3 manage.py migrate django_celery_results --noinput
echo 'deploying backend server'
python3 manage.py runserver 0.0.0.0:5000
