import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')

# Create the Celery app instance
app = Celery('alx_backend_graphql')

# Load task configuration from Django settings, using a 'CELERY_' prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps (e.g., from crm/tasks.py)
app.autodiscover_tasks()