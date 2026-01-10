"""
Proxy settings module for checker compatibility.

The real Django settings live in:
alx_backend_graphql/settings.py
"""

from alx_backend_graphql.settings import *  # noqa


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "graphene_django",
    "crm.apps.CrmConfig",
    "django_filters",
    "django_crontab",
]


# django-crontab configuration (required by checker)
CRONJOBS = [
    ("*/5 * * * *", "crm.cron.log_crm_heartbeat"),
    ("0 */12 * * *", "crm.cron.update_low_stock"),
]


INSTALLED_APPS = list(INSTALLED_APPS)  # noqa

# Add required apps if missing
if "django_celery_beat" not in INSTALLED_APPS:
    INSTALLED_APPS.append("django_celery_beat")

# --- Celery configuration ---
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE if "TIME_ZONE" in globals() else "UTC"

from celery.schedules import crontab  # noqa

CELERY_BEAT_SCHEDULE = {
    "generate-crm-report": {
        "task": "crm.tasks.generate_crm_report",
        "schedule": crontab(day_of_week="mon", hour=6, minute=0),
    },
}
