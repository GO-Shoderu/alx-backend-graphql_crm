#!/bin/bash

# Absolute paths are critical for cron jobs
PROJECT_DIR="/home/gosh/Documents/alx/be/alx-backend-graphql_crm"
PYTHON="/home/gosh/Documents/alx/be/alx-backend-graphql_crm/.venv/bin/python"
MANAGE_PY="$PROJECT_DIR/manage.py"
LOG_FILE="/tmp/customer_cleanup_log.txt"

DELETED_COUNT=$(
  $PYTHON $MANAGE_PY shell <<'EOF'
from datetime import timedelta
from django.utils import timezone
from django.db.models import Max, Q
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)

# Customers who have never ordered OR whose last order is older than 1 year
qs = Customer.objects.annotate(
    last_order=Max("orders__created_at")
).filter(
    Q(last_order__lt=one_year_ago) | Q(last_order__isnull=True)
)

count = qs.count()
qs.delete()
print(count)
EOF
)

echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: $DELETED_COUNT" >> "$LOG_FILE"
