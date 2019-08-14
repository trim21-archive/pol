import pytest
from starlette.testclient import TestClient

import app.fast
from app.db.database import db


@pytest.fixture(autouse=True)
def client():
    with TestClient(app.fast.app) as test_client:
        yield test_client
    client.app.dependency_overrides = {}


@pytest.fixture()
def mysql():
    with db.allow_sync():
        yield db
