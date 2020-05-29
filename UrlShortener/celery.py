import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrlShortener.settings')
app = Celery('UrlShortener')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()