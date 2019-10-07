import redis
import pytest
from starlette.testclient import TestClient

import app.fast
from app.core import config
from app.db.database import db


@pytest.fixture()
def client():
    with TestClient(app.fast.app) as test_client:
        yield test_client
    app.fast.app.dependency_overrides = {}


@pytest.fixture()
def redis_client():
    with redis.StrictRedis.from_url(config.REDIS_URI) as redis_client:
        yield redis_client


def pytest_sessionstart(session: pytest.Session):
    """Called after the Session object has been created and

    before performing collection and entering the run test loop.

    Args:
        session: pytest Session object
    """
    db.set_allow_sync(True)
