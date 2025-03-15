# pixventure_back/celery.py
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pixventure_back.settings")

app = Celery("pixventure_back")

# Load task modules from all registered Django apps.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
