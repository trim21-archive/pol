import json

import pytest
import aioredis
from aiologger import Logger

from app.log import setup_logger
from app.core import config

KEY = f"{config.APP_NAME}-log"


@pytest.mark.asyncio
async def test_send_event():
    redis_client = await aioredis.create_redis(config.REDIS_URI)
    await redis_client.delete(KEY)

    logger: Logger = await setup_logger()
    await logger.info("logger info", extra={"headers": {"x-request-id": "233"}})
    await logger.shutdown()

    assert 1 == await redis_client.llen(KEY)
    e = await redis_client.lpop(KEY)
    data = json.loads(e)
    assert data["headers"]["x-request-id"] == "233"
    assert data["@metadata"] == {"beat": "py_logging", "version": "dev"}
    assert data["msg"] == "logger info"
    redis_client.close()
    await redis_client.wait_closed()
