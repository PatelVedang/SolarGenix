import os
from django.conf import settings
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")
app = Celery("proj")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(settings.INSTALLED_APPS)