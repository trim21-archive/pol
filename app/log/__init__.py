import sys
import logging
import platform

import redis
from loguru import logger

from app.core import config
from app.log.sink import Sink


def setup_logger():
    logger.add(
        sink,
        enqueue=True,
        level=logging.INFO,
        filter=lambda record: 'event' in record['extra']
    )
    if config.DEBUG:
        logger.add(sys.stdout, level=logging.DEBUG, colorize=True)
    else:
        logger.add(sys.stdout, level=logging.INFO, colorize=True)

    logger.debug('setup logger')


sink = Sink(
    client=redis.StrictRedis.from_url(config.REDIS_URI),
    key=f'{config.APP_NAME}-log',
    extra={
        '@metadata': {
            'beat': 'py_logging',
            'version': config.COMMIT_REF,
        },
        'version': config.COMMIT_REF,
        'platform': platform.platform(),
    },
    tz=config.TIMEZONE,
)
logger.remove()
setup_logger()
