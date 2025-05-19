# project/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')

app = Celery('proj')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'clean-expired-tokens-daily': {
        'task': 'auth_api.tasks.clean_expired_tokens',
        'schedule': crontab(minute=0, hour=0),  # every day at midnight
    },
}