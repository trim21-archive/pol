from starlette.testclient import TestClient


def test_doc_html(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_json(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"


def test_bgm_tv_user_calendar(client: TestClient):
    response = client.get("/api.v1/calendar/bgm.tv/1", allow_redirects=False)
    assert response.headers["location"] == "https://api.bgm38.com/bgm.tv/v1/calendar/1"
