import json

from aioredis import Redis
from aiologger.loggers.json import ExtendedLogRecord
from aiologger.handlers.base import Handler

from app.core import config


class RedisHandler(Handler):
    def __init__(
        self, redis_client, key=f"{config.APP_NAME}-log", *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.key = key
        self.redis_client: Redis = redis_client

    @property
    def initialized(self):
        return not self.redis_client.closed

    async def emit(self, record: ExtendedLogRecord) -> None:
        await self.redis_client.rpush(self.key, self.format(record))

    async def close(self) -> None:
        self.redis_client.close()
        await self.redis_client.wait_closed()

    @staticmethod
    def format(record: ExtendedLogRecord):
        o = {
            "msg": record.get_message(),
            "logged_at": record.created,
            "line_number": record.lineno,
            "file": record.pathname,
            "function": record.funcName,
            "level": record.levelname,
            "module": record.module,
            "kwargs": record.args,
            **record.extra,
        }
        return json.dumps(o, ensure_ascii=False)
