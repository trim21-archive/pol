import pytest
from starlette.testclient import TestClient

import app.fast
from app.db.database import db


@pytest.fixture(autouse=True)
def client():
    with TestClient(app.fast.app) as test_client:
        yield test_client
    app.fast.app.dependency_overrides = {}


@pytest.fixture()
def mysql():
    with db.allow_sync():
        yield db


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    'session start'
    db.set_allow_sync(True)
