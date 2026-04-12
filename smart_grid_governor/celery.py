import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_grid_governor.settings')

app = Celery('smart_grid_governor')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()