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
    with redis.StrictRedis.from_url(config.REDIS_URI) as redis_client:
        yield redis_client
