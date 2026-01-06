#!/bin/bash

# Absolute paths are critical for cron jobs
PROJECT_DIR="/home/gosh/Documents/alx/be/alx-backend-graphql_crm"
PYTHON="/home/gosh/Documents/alx/be/alx-backend-graphql_crm/.venv/bin/python"
MANAGE_PY="$PROJECT_DIR/manage.py"
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Run Django shell command
DELETED_COUNT=$(
  $PYTHON $MANAGE_PY shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)

deleted, _ = Customer.objects.filter(
    orders__isnull=True,
    created_at__lt=one_year_ago
).delete()

print(deleted)
EOF
)

# Log result with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: $DELETED_COUNT" >> $LOG_FILE
