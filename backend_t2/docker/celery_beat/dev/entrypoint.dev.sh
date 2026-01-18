#!/bin/env bash

echo 'deploying celery beat server'
python3 -m celery -A celery_settings:app beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler