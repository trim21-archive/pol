import json
import platform

from aioredis import Redis, create_redis_pool
from aiologger.loggers.json import ExtendedLogRecord
from aiologger.handlers.base import Handler

from app.core import config

key = f"{config.APP_NAME}-log"
extra = {
    "@metadata": {"beat": "py_logging", "version": config.COMMIT_REF},
    "version": config.COMMIT_REF,
    "platform": platform.platform(),
}
tz = (config.TIMEZONE,)


class RedisHandler(Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client: Redis = None

    async def init(self):
        self.redis_client = await create_redis_pool(
            config.REDIS_URI, password=config.REDIS_PASSWORD
        )

    async def emit(self, record: ExtendedLogRecord) -> None:
        await self.redis_client.rpush(key, self.format(record))

    async def close(self) -> None:
        self.redis_client.close()

    @staticmethod
    def format(record: ExtendedLogRecord):
        o = {
            "@metadata": {"beat": "py_logging", "version": config.COMMIT_REF},
            "version": config.COMMIT_REF,
            "platform": platform.platform(),
            "msg": record.get_message(),
            "logged_at": record.created,
            "line_number": record.lineno,
            "function": record.funcName,
            "level": record.levelname,
            "module": record.module,
            "process": record.process,
        }
        o.update(record.extra)
        return json.dumps(o)
