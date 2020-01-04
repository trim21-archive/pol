import re
import json
import datetime

import mock
from yarl import URL
from aioresponses import CallbackResult, aioresponses
from starlette.testclient import TestClient

from app.core import config
from app.db_models import UserToken
from app.db.database import objects
from app.api.bgm_tv_auto_tracker.auth import get_current_user


def test_oauth_redirect(client: TestClient):
    response = client.get('/bgm-tv-auto-tracker/api.v1/auth', allow_redirects=False)
    assert response.status_code == 302

    assert response.headers['location'] == config.BgmTvAutoTracker.oauth_url


def test_refresh_token(client: TestClient, mock_aiohttp: aioresponses):
    auth_time = datetime.datetime.now()

    def refresh_token_cb(url, data: dict, **kwargs):
        for key in data.keys():
            assert key in {
                'grant_type',
                'refresh_token',
                'client_id',
                'redirect_uri',
                'client_secret',
            }

        return CallbackResult(
            body=json.dumps({
                'access_token': 'new_access_token',
                'expires_in': 505,
                'token_type': 'Bearer',
                'scope': '',
                'refresh_token': 'some_new_token',
            }),
            headers={'Date': datetime.datetime.now().isoformat()},
        )

    def api_user_info_cb(url, **kwargs):
        return CallbackResult(
            body=json.dumps({
                'id': 233,
                'url': 'http://bgm.tv/user/233',
                'username': 'some_username',
                'nickname': 'some_nickname',
                'avatar': {
                    'large': 'http://lain.bgm.tv/pic/user/l/000/28/76/287622.jpg',
                    'medium': 'http://lain.bgm.tv/pic/user/m/000/28/76/287622.jpg',
                    'small': 'http://lain.bgm.tv/pic/user/s/000/28/76/287622.jpg',
                },
                'sign': '站外点格子工具 https://bgm.tv/group/topic/346446 . ...',
                'usergroup': 10,
            })
        )

    refresh_token_cb = mock.Mock(side_effect=refresh_token_cb)
    api_user_info_cb = mock.Mock(side_effect=api_user_info_cb)
    mock_aiohttp.post('https://bgm.tv/oauth/access_token', callback=refresh_token_cb)
    mock_aiohttp.get(
        re.compile(r'https://api.bgm.tv/user/.*'),
        callback=api_user_info_cb,
    )

    with objects.allow_sync():
        UserToken.replace(
            user_id=233,
            token_type='Bearer',
            expires_in=6400,
            auth_time=1560242743,
            access_token='some_access_token',
            refresh_token='some_token',
            username='some_username',
            nickname='some_nickname',
            usergroup=10,
            scope='',
        ).execute()

    async def mock_get_current_user():
        return await objects.get(UserToken, user_id=233)

    client.app.dependency_overrides[get_current_user] = mock_get_current_user
    r = client.post('/bgm-tv-auto-tracker/api.v1/refresh')
    assert r.status_code == 200, r.text
    refresh_token_cb.assert_called_once_with(
        URL('https://bgm.tv/oauth/access_token'),
        data={
            'grant_type': 'refresh_token',
            'refresh_token': 'some_token',
            'client_id': config.BgmTvAutoTracker.APP_ID,
            'redirect_uri': config.BgmTvAutoTracker.callback_url,
            'client_secret': config.BgmTvAutoTracker.APP_SECRET,
        }
    )
    api_user_info_cb.assert_called_once_with(
        URL('https://api.bgm.tv/user/233'), allow_redirects=True
    )

    with objects.allow_sync():
        user: UserToken = UserToken.get(user_id=233)
        assert user.access_token == 'new_access_token', 'access token mismatch'
        assert user.refresh_token == 'some_new_token', 'refresh token mismatch'
        assert user.username == 'some_username', 'username mismatch'
        assert user.nickname == 'some_nickname', 'nickname mismatch'
        assert user.auth_time == int(auth_time.timestamp()), 'auth time mismatch'
        assert user.expires_in == 505, 'expires time mismatch'
        assert user.usergroup == 10, 'usergroup mismatch'
