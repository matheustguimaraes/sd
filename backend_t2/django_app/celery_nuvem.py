"""Base Celery App."""

import os

import django
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings")

django.setup()

app = Celery("django_app")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(
    settings.INSTALLED_APPS,
)
app.conf.worker_hijack_root_logger = False


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
