"""
this test will test both logger and msgpack
"""
import logging

import redis
import msgpack

from app.log import sink, logger
from app.core import config

KEY = f"{config.APP_NAME}-log"


def test_send_event(redis_client: redis.StrictRedis):

    logger.remove()
    logger.add(
        sink, level=logging.INFO, filter=lambda record: "event" in record["extra"],
    )

    bind = {
        "event": "test_event",
        "kwargs": {"arg1": 1, "arg2": [2], "arg3": "你好"},
    }
    redis_client.delete(KEY)
    logger.bind(**bind).info("logger info")
    assert redis_client.llen(KEY) == 1
    e = redis_client.lpop(KEY)
    data = msgpack.loads(e, raw=False)
    for key, value in bind.items():
        assert data[key] == value
    assert data["@metadata"] == {"beat": "py_logging", "version": "dev"}
    assert data["msg"] == "logger info"
