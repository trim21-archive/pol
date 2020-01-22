import kombu
from celery import Celery

from app.core import config

broker = f'amqp://{config.RABBITMQ_USER}:{config.RABBITMQ_PASS}@{config.RABBITMQ_ADDR}/'
celery = Celery('worker', broker=broker)

celery.conf.task_routes = {'app.worker.*': 'celery-www-tasks'}
celery.conf.update(
    task_queues=[kombu.Queue('celery-www-tasks', exchange='celery-www-tasks')],
    worker_concurrency='4',
)
