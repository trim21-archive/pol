import asyncio
from typing import Callable

from loguru import logger

from app.core import config
from app.core.celery_app import celery
from app.video_website_spider import Dispatcher

if config.DSN:  # pragma: no cover
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    logger.debug('setup sentry for celery')
    sentry_sdk.init(
        dsn=config.DSN,
        release=config.COMMIT_SHA,
        integrations=[CeleryIntegration()],
    )

dispatcher = Dispatcher()


@celery.task
def submit_bangumi(subject_id: int, url: str):
    dispatcher.subject(subject_id, url)


@celery.task
def submit_ep(ep_id: int, url: str):
    dispatcher.ep(ep_id, url)


async def submit_task(func: Callable, args=None, kwargs=None):
    asyncio.create_task(
        asyncio.get_event_loop().run_in_executor(
            None, lambda: celery.send_task(func.__name__, args, kwargs)
        )
    )
