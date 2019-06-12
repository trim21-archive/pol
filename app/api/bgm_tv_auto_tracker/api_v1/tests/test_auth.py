import json
import datetime

import mock
import urllib3.response
from asynctest import CoroutineMock
from requests_async import Response
from requests.structures import CaseInsensitiveDict
from starlette.testclient import TestClient

from app.core import config
from app.db_models import UserToken
from app.db.database import objects
from app.api.bgm_tv_auto_tracker.auth import get_current_user


def mock_response(headers, body):
    content = body.encode()
    r = Response()
    r.raw = urllib3.response.HTTPResponse(body=content)
    r._content = content
    r.headers = CaseInsensitiveDict(headers)

    corofunc = CoroutineMock(return_value=r)
    return corofunc


def test_oauth_redirect(client: TestClient):
    response = client.get(
        '/bgm-tv-auto-tracker/api.v1/auth', allow_redirects=False
    )
    assert response.status_code == 302
    from app.core import config

    assert response.headers['location'] == config.BgmTvAutoTracker.oauth_url


def test_oauth_callback(client: TestClient):
    auth_time = datetime.datetime.now()
    mock_get = mock_response(
        {'date': auth_time.isoformat()},
        json.dumps({
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
        }),
    )
    mock_post = mock_response(
        {'date': auth_time.isoformat()},
        json.dumps({
            'access_token': 'some_access_token',
            'expires_in': 6400,
            'token_type': 'Bearer',
            'user_id': 233,
            'refresh_token': 'some_token',
        }),
    )

    with objects.allow_sync():
        UserToken.delete().execute()

    with mock.patch('requests_async.post',
                    mock_post), mock.patch('requests_async.get', mock_get):
        r = client.get(
            '/bgm-tv-auto-tracker/api.v1/oauth_callback',
            params={'code': '233'}
        )
        assert r.status_code == 200, 'response code not 200'
        assert 'bgm-tv-auto-tracker' in r.cookies
        me_resp = client.get('/bgm-tv-auto-tracker/api.v1/me').json()
        mock_post.assert_awaited_once_with(
            'https://bgm.tv/oauth/access_token',
            data={
                'code': '233',
                'client_id': config.BgmTvAutoTracker.APP_ID,
                'grant_type': 'authorization_code',
                'redirect_uri': config.BgmTvAutoTracker.callback_url,
                'client_secret': config.BgmTvAutoTracker.APP_SECRET,
            },
        )
        mock_get.assert_awaited_once_with('https://api.bgm.tv/user/233')

    assert me_resp['access_token'] == 'some_access_token', (
        'access token mismatch in /me'
    )
    assert me_resp['expires_in'] == 6400, 'expires time mismatch in /me'
    assert me_resp['token_type'] == 'Bearer', 'token type mismatch in /me'
    assert me_resp['user_id'] == 233, 'user_id mismatch in /me'

    with objects.allow_sync():
        user: UserToken = UserToken.get(user_id=233)
        assert user.access_token == 'some_access_token', 'access token mismatch'
        assert user.refresh_token == 'some_token', 'refresh token mismatch'
        assert user.username == 'some_username', 'username mismatch'
        assert user.nickname == 'some_nickname', 'nickname mismatch'
        assert user.auth_time == int(
            auth_time.timestamp()
        ), 'auth time mismatch'
        assert user.expires_in == 6400, 'expires time mismatch'
        assert user.usergroup == 10, 'usergroup mismatch'


def test_refresh_token(client: TestClient):
    auth_time = datetime.datetime.now()

    mock_get = mock_response(
        {'date': auth_time.isoformat()},
        json.dumps({
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
        }),
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
    mock_post = mock_response(
        {'date': auth_time.isoformat()},
        json.dumps({
            'access_token': 'new_access_token',
            'expires_in': 505,
            'token_type': 'Bearer',
            'scope': '',
            'refresh_token': 'some_new_token',
        }),
    )

    with mock.patch('requests_async.post',
                    mock_post), mock.patch('requests_async.get', mock_get):
        r = client.post('/bgm-tv-auto-tracker/api.v1/refresh')
        assert r.status_code == 200, r.text
        mock_post.assert_awaited_once_with(
            'https://bgm.tv/oauth/access_token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': 'some_token',
                'client_id': config.BgmTvAutoTracker.APP_ID,
                'redirect_uri': config.BgmTvAutoTracker.callback_url,
                'client_secret': config.BgmTvAutoTracker.APP_SECRET,
            }
        )
        mock_get.assert_awaited_once_with('https://api.bgm.tv/user/233')

    with objects.allow_sync():
        user: UserToken = UserToken.get(user_id=233)
        assert user.access_token == 'new_access_token', 'access token mismatch'
        assert user.refresh_token == 'some_new_token', 'refresh token mismatch'
        assert user.username == 'some_username', 'username mismatch'
        assert user.nickname == 'some_nickname', 'nickname mismatch'
        assert user.auth_time == int(
            auth_time.timestamp()
        ), 'auth time mismatch'
        assert user.expires_in == 505, 'expires time mismatch'
        assert user.usergroup == 10, 'usergroup mismatch'

    client.app.dependency_overrides = {}
