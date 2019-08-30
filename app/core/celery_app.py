import kombu
from celery import Celery

from app.core import config

celery = Celery(
    'worker',
    broker=f'amqp://{config.RABBITMQ_USER}:{config.RABBITMQ_PASS}'
    f'@{config.RABBITMQ_ADDR}//'
)

celery.conf.task_routes = {'app.worker.*': 'celery-www-tasks'}
celery.conf.update(
    task_queues=[kombu.Queue('celery-www-tasks', exchange='celery-www-tasks')],
    worker_concurrency='4',
)
