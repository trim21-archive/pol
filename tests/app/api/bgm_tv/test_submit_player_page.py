import mock
import pytest
from starlette.testclient import TestClient

import app.worker
from app.db_models import sa
from app.api.auth.api_v1 import get_current_user


@pytest.mark.skip
@pytest.mark.parametrize(
    "url", ["/bgm.tv/api.v0/subject/player/233593", "/bgm.tv/api.v0/ep/player/233593",]
)
def test_submit_subject_id_require_auth(client: TestClient, url):
    r = client.put(
        url, json={"bangumi_id": "string", "source": "bilibili", "subject_id": 288,}
    )
    assert r.status_code == 403, "user submit subject_id don't need auth"


@pytest.mark.skip
def test_submit_subject_url(client: TestClient,):
    async def mock_get_current_user():
        return sa.UserToken(user_id=233)

    client.app.dependency_overrides[get_current_user] = mock_get_current_user
    subject_id = 233593
    url = "https://www.bilibili.com/bangumi/play/ep262002"
    with mock.patch("app.worker.submit_bangumi"):
        r = client.put(f"/bgm.tv/api.v0/subject/player/{subject_id}", json={"url": url})
        assert r.status_code == 200, r.text
        app.worker.submit_bangumi.delay.assert_called_once_with(subject_id, url)
    assert r.status_code == 200, r.text


@pytest.mark.skip
def test_submit_ep_url(client: TestClient,):
    async def mock_get_current_user():
        return sa.UserToken(user_id=233)

    client.app.dependency_overrides[get_current_user] = mock_get_current_user
    ep_id = 2891213
    url = "https://www.bilibili.com/bangumi/play/ep276479"
    with mock.patch("app.worker.submit_ep"):
        r = client.put(f"/bgm.tv/api.v0/ep/player/{ep_id}", json={"url": url})
        assert r.status_code == 200, r.text
        app.worker.submit_ep.delay.assert_called_once_with(ep_id, url)

    assert r.status_code == 200, r.text
