import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')

app = Celery('ecommerce_project')

app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()

app.conf.beat_schedule = {
    'restore-cart-items': {
        'task': 'cart.tasks.restore_cart_items_to_inventory',
        'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    },
} 