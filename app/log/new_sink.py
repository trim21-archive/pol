import json
import platform

from aioredis import Redis, create_redis_pool
from aiologger.records import LogRecord
from aiologger.handlers.streams import Handler

from app.core import config

key = (f"{config.APP_NAME}-log",)
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

    async def emit(self, record: LogRecord) -> None:
        if self.redis_client is None:
            self.redis_client = await create_redis_pool(
                config.REDIS_URI, password=config.REDIS_PASSWORD
            )
        await self.redis_client.rpush(
            key, json.dumps({"msg": record.get_message(), "@metadata": extra})
        )

    async def close(self) -> None:
        self.redis_client.close()
