from __future__ import absolute_import, unicode_literals
import os
from celery import Celery




# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoprj.settings')

app = Celery('todoprj')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_connection_retry_on_startup = True

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery Beat schedule configuration
app.conf.beat_schedule = {
    'send-reminders-every-minute': {
        'task': 'todoapp.tasks.send_reminders',
        'schedule': 60.0,  # Every minute
    },
}
