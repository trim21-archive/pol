import platform

from aioredis import create_redis_pool
from aiologger.loggers.json import JsonLogger

from app.core import config
from app.log.new_sink import RedisHandler


async def setup_logger():
    logger = JsonLogger(
        name="pol",
        extra={
            "@metadata": {"beat": "py_logging", "version": config.COMMIT_REF,},
            "version": config.COMMIT_REF,
            "platform": platform.platform(),
        },
    )

    h = RedisHandler(
        redis_client=await create_redis_pool(config.REDIS_URI),
        key=f"{config.APP_NAME}-log",
    )
    logger.add_handler(h)

    return logger
