from app.core.celery_app import celery
from app.video_website_spider import Dispatcher


@celery.task(acks_late=True)
def test_celery(word: str):
    return f'test task return {word}'


dispatcher = Dispatcher()


@celery.task
def submit_bangumi(subject_id: int, url: str):
    dispatcher.subject(subject_id, url)


@celery.task
def submit_ep(ep_id: int, url: str):
    dispatcher.ep(ep_id, url)
