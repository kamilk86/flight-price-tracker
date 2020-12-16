from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faretracker_project.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1') # This is only for windows so that celery worker does not raise KeyError


app = Celery('faretracker_project', broker='redis://localhost:6379')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
