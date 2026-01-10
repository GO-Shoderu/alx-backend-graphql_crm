# CRM Celery Setup

This project uses Celery + Celery Beat with Redis for scheduling background jobs.

## Setup Instructions

### 1. Install Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# MacOS (using Homebrew)
brew install redis
Start Redis service:

sudo service redis-server start

Install Python dependencies:
pip install -r requirements.txt

2. Run Database Migrations

Apply all Django migrations:

python manage.py migrate

3. Start Celery Worker

Run the Celery worker for the CRM app:

celery -A crm worker -l info


This will process background tasks for your CRM application.

4. Start Celery Beat

Start Celery Beat to handle scheduled tasks:

celery -A crm beat -l info


This will schedule periodic tasks defined in the CRM app.

5. Verify Logs

Check the log file to ensure tasks are running properly:

cat /tmp/crm_report_log.txt


You should see logs indicating that the heartbeat and scheduled tasks are being processed.
