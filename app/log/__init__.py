import logging
import platform

import redis
from loguru import logger

from app.core import config
from app.log.sink import Sink


def setup_logger():
    sink = Sink(
        client=redis.StrictRedis.from_url(config.REDIS_URI),
        key=f'{config.APP_NAME}-log',
        extra={
            '@metadata': {'beat': 'py_logging'},
            'version': config.COMMIT_SHA,
            'platform': platform.platform(),
        },
        tz=config.TIMEZONE,
    )
    logger.add(
        sink,
        enqueue=True,
        level=logging.INFO,
    )


setup_logger()
