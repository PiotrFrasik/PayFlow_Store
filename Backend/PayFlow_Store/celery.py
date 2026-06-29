import os
from celery import Celery

# Main configuration for celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PayFlow_Store.settings')

app = Celery('PayFlow_Store')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Finding tasks for celery
app.autodiscover_tasks()