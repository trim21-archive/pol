import json

import pytest
from aiologger import Logger

from app.log import setup_logger
from app.core import config

KEY = f"{config.APP_NAME}-log"


@pytest.mark.asyncio
async def test_send_event(redis_client):
    logger: Logger = await setup_logger()
    await logger.info("logger info", extra={"headers": {"x-request-id": "233"}})
    await logger.shutdown()

    assert 1 == redis_client.llen(KEY)
    e = redis_client.lpop(KEY)
    data = json.loads(e)
    assert data["headers"]["x-request-id"] == "233"
    assert data["@metadata"] == {"beat": "py_logging", "version": "dev"}
    assert data["msg"] == "logger info"
