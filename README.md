# Celery Task for Generating CRM Reports

## Install Redis and dependencies

Ensure Redis is installed and running locally.

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Run migrations

```bash
python manage.py migrate
```

## Start Celery worker

```bash
celery -A crm worker -l info
```

## Start Celery Beat

```bash
celery -A crm beat -l info
```

## Verify logs

Check the generated CRM report log:

```bash
cat /tmp/crm_report_log.txt
```
