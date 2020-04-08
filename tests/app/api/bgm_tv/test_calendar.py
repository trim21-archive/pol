from starlette.testclient import TestClient


def test_get_user_watching_calendar_200(client: TestClient):
    r = client.get("/api.v1/calendar/bgm.tv/1")
    assert r.status_code == 200, "existing user return 200"
    assert "text/calendar" in r.headers["content-type"]


def test_get_user_watching_calendar_404(client: TestClient):
    r = client.get("/api.v1/calendar/bgm.tv/0")
    assert r.status_code == 404, "non existing user return 404"
