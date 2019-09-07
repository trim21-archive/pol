import pytest
import pytest_mock
from starlette.testclient import TestClient

import app.worker
from app.db_models import UserToken
from app.api.bgm_tv_auto_tracker.auth import get_current_user


@pytest.mark.parametrize(
    'url', [
        '/bgm.tv/api.v0/player/subject/233593',
        '/bgm.tv/api.v0/player/ep/233593',
    ]
)
def test_submit_subject_id_require_auth(client: TestClient, url):
    r = client.post(
        url, json={
            'bangumi_id': 'string',
            'source': 'bilibili',
            'subject_id': 288,
        }
    )
    assert r.status_code == 403, 'user submit subject_id don\'t need auth'


def test_submit_subject_url(
    client: TestClient,
    mocker: pytest_mock.MockFixture,
):
    async def mock_get_current_user():
        return UserToken(user_id=233)

    client.app.dependency_overrides[get_current_user] = mock_get_current_user
    subject_id = 233593
    url = 'https://www.bilibili.com/bangumi/play/ep262002'
    with mocker.patch('app.worker.submit_bangumi'):
        r = client.post(
            f'/bgm.tv/api.v0/player/subject/{subject_id}', json={'url': url}
        )
        app.worker.submit_bangumi.delay.assert_called_once_with(subject_id, url)
    assert r.status_code == 200, r.text


def test_submit_ep_url(
    client: TestClient,
    mocker: pytest_mock.MockFixture,
):
    async def mock_get_current_user():
        return UserToken(user_id=233)

    client.app.dependency_overrides[get_current_user] = mock_get_current_user
    ep_id = 2891213
    url = 'https://www.bilibili.com/bangumi/play/ep276479'
    with mocker.patch('app.worker.submit_ep'):
        r = client.post(f'/bgm.tv/api.v0/player/ep/{ep_id}', json={'url': url})
        app.worker.submit_ep.delay.assert_called_once_with(ep_id, url)

    assert r.status_code == 200, r.text
