import os
from celery import Celery

# Use the project settings as the primary settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql.settings")

app = Celery("crm")

# Read CELERY_* settings from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in installed apps
app.autodiscover_tasks()
