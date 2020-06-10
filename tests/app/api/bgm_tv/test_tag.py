from starlette.testclient import TestClient


def test_search_by_tag(client: TestClient):
    response = client.get(
        "/bgm.tv/api.v1/subjects", params={"tag": ("漫改", "治愈"), "limit": 4},
    )
    assert response.status_code == 200
    assert response.json()


def test_search_by_tag_limit_out_of_range(client: TestClient):
    response = client.get(
        "/bgm.tv/api.v1/subjects", params={"tag": ("漫改", "治愈"), "limit": 51},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_search_require_text(client: TestClient):
    response = client.get("/bgm.tv/api.v1/subjects")
    assert response.status_code == 422
    assert "detail" in response.json()


def test_search_filter_type(client: TestClient):
    response = client.get(
        "/bgm.tv/api.v1/subjects",
        params={"tag": ("漫改", "治愈"), "limit": 4, "subject_type": "Anime"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["subjects"]
    for subject in data["subjects"]:
        assert (
            subject["subject_type"] == "Anime"
        ), "response item should only be `Anime`"
