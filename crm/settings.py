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
