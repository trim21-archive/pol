from starlette.testclient import TestClient


def test_map_id(client: TestClient):
    response = client.get("/api.v1/view_ip/subject/8")
    assert response.status_code == 200
    response.json()


def test_subject_no_map(client: TestClient):
    response = client.get("/api.v1/view_ip/subject/3000000")
    assert response.status_code == 404
