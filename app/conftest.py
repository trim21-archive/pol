import pytest
from starlette.testclient import TestClient

import app.fast


@pytest.fixture(autouse=True)
def client():
    with TestClient(app.fast.app) as client:
        yield client
