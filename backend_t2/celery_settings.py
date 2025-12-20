"""Base Celery App."""

import os

import django
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings")

django.setup()

app = Celery("django_app")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.worker_hijack_root_logger = False
