from starlette.testclient import TestClient

from app.db_models import UserToken, UserSubmitBangumi
from app.db.database import objects
from app.api.bgm_tv_auto_tracker.auth import get_current_user


def test_refresh_token_require_auth(client: TestClient):
    r = client.post(
        '/bgm-tv-auto-tracker/api.v1/submit/subject_id',
        json={
            'bangumi_id': 'string',
            'source': 'bilibili',
            'subject_id': 288,
        }
    )
    assert r.status_code == 403, 'user submit subject_id don\'t need auth'


def test_refresh_token(client: TestClient):
    async def mock_get_current_user():
        return UserToken(user_id=233)

    client.app.dependency_overrides[get_current_user] = mock_get_current_user

    r = client.post(
        '/bgm-tv-auto-tracker/api.v1/submit/subject_id',
        json={
            'bangumi_id': 'string',
            'source': 'bilibili',
            'subject_id': 288,
        }
    )
    assert r.status_code == 200, r.text

    with objects.allow_sync():
        UserSubmitBangumi.get(
            user_id=233, bangumi_id='string', source='bilibili', subject_id=288
        )

    client.app.dependency_overrides = {}


def test_refresh_token_bad_input(client: TestClient):
    async def mock_get_current_user():
        return UserToken(user_id=233)

    client.app.dependency_overrides[get_current_user] = mock_get_current_user

    r = client.post(
        '/bgm-tv-auto-tracker/api.v1/submit/subject_id',
        json={
            'bangumi_id_': 'string',
            'source': 'bilibili',
            'subject_id': 288,
        }
    )
    assert r.status_code == 422, r.text

    with objects.allow_sync():
        UserSubmitBangumi.get(
            user_id=233, bangumi_id='string', source='bilibili', subject_id=288
        )

    client.app.dependency_overrides = {}
