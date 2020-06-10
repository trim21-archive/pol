import redis
import pytest
from starlette.testclient import TestClient

import app.fast
from app.core import config


@pytest.fixture()
def client():
    with TestClient(app.fast.app) as test_client:
        yield test_client
    app.fast.app.dependency_overrides = {}


@pytest.fixture()
def redis_client():
    with redis.Redis(
        host=config.REDIS_HOST, password=config.REDIS_PASSWORD
    ) as redis_client:
        redis_client.flushdb()
        yield redis_client
        redis_client.flushdb()
