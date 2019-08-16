import sys
import asyncio
import platform
from logging import INFO, StreamHandler, getLogger

import aioredis

from app.core import config

from .handler import LogstashHandler


async def setup_async_handler(lo):
    redis_client = await aioredis.create_redis_pool(
        config.REDIS_URI,
        password=config.REDIS_PASSWORD,
        db=0,
        timeout=1,
    )
    aio_log_handler = LogstashHandler(
        client=redis_client,
        key=f'{config.APP_NAME}-log',
        level=INFO,
        extra={
            '@metadata': {'beat': 'py_logging'},
            'version': config.COMMIT_SHA,
            'platform': platform.platform(),
        },
        tz=config.TIMEZONE,
    )
    aio_log_handler.start(lo)
    getLogger('app').addHandler(aio_log_handler)


loop = asyncio.get_event_loop()

logger = getLogger('app')
if not loop.is_running():
    # in web server, loop is running, so set async handler
    loop.run_until_complete(setup_async_handler(loop))

log_level = 'INFO'
logger.setLevel(log_level)
logger.addHandler(StreamHandler(sys.stdout))
