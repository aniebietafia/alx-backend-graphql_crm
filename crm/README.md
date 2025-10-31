# Configuration and Usage Guide for CRM System
This guide outlines the steps to set up and run the CRM application, including its scheduled tasks with Celery and Celery Beat.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.8+ and pip
- Git
- Redis Server

## Setup Steps
1. Install Redis and dependencies
2. Run migrations (python manage.py migrate)
3. Start Celery worker (celery -A crm worker -l info).
4. Start Celery Beat (celery -A crm beat -l info).
5. Verify logs in /tmp/crm_report_log.txt.

## Setup Instructions
1. Clone the Repository
```bash
git clone <your-repository-url>
cd <your-project-directory>
```
2. Install Redis and dependencies
Redis is required as the message broker for Celery.
- On macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```
- On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```
3. Install Python Dependencies: Install all required packages, including Django, Celery, and django-celery-beat.
```bash
pip install -r requirements.txt
```
4. Run Database Migrations
This will create the necessary database tables, including those for Celery Beat.
```bash
python manage.py migrate
```

## Running the Application and Services
You need to run three separate processes in different terminal windows: the Django server, the Celery worker, and the Celery Beat scheduler.

1. Terminal 1: Run the Django Server (Optional, for development)
```bash
python manage.py runserver
```
2. Terminal 2: Run the Celery Worker: The worker process executes the tasks.
```bash
# The project name is 'alx_backend_graphql'
celery -A alx_backend_graphql worker -l info
```

3. Terminal 3: Run the Celery Beat Scheduler
The scheduler (Beat) triggers tasks at their scheduled times.
```bash
# The project name is 'alx_backend_graphql'
celery -A alx_backend_graphql beat -l info
```

## Verifying the Report

The `generate_crm_report` task is scheduled to run every Monday at 6:00 AM (as per the schedule in `settings.py`).

To verify that it has run, you can check the log file:
```bash
cat /tmp/crm_report_log.txt
```

You should see entries like this:
```bash
2025-11-03 06:00:00 - Report: 150 customers, 450 orders, 52341.75 revenue
```