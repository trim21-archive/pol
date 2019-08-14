from celery import Celery

from app.core import config

celery = Celery(
    'worker',
    broker=f"redis://:{config.REDIS_PASSWORD or ''}@{config.REDIS_HOST}:6379/0"
)
celery.conf.task_routes = {'app.worker.*': 'celery-www-queue'}
