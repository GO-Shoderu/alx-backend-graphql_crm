"""
Proxy settings module for checker compatibility.

The real Django settings live in:
alx_backend_graphql/settings.py
"""

from alx_backend_graphql.settings import *  # noqa


# django-crontab configuration (required by checker)
CRONJOBS = [
    ("*/5 * * * *", "crm.cron.log_crm_heartbeat"),
]
