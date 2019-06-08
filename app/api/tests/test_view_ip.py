import pytest
from starlette.testclient import TestClient

from app.fast import app


@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client


def test_map_id(client: TestClient):
    response = client.get('/api.v1/view_ip/subject/8')
    assert response.status_code == 200
    response.json()


def test_subject_no_map(client: TestClient):
    response = client.get('/api.v1/view_ip/subject/290000')
    assert response.status_code == 404
    assert response.json()['detail'] == 'subject not found'
