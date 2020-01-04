from aioresponses import aioresponses
from starlette.testclient import TestClient

from app.api.auth.api_v1 import OAUTH_URL
from tests.mock_aiohttp.app import mock_bgm_auth_app


def test_oauth_redirect(client: TestClient):
    r = client.get('/auth/api.v1/bgm.tv_auth', allow_redirects=False)
    assert OAUTH_URL == r.headers['location']
    assert r.status_code == 307


def test_oauth_callback_no_query_redirect(client: TestClient):
    r = client.get('/auth/api.v1/bgm.tv_oauth_callback', allow_redirects=False)
    assert r.headers['location'] == './bgm.tv_auth'
    assert r.status_code == 307


def test_oauth_callback_no_query_code(client: TestClient):
    r = client.get('/auth/api.v1/bgm.tv_oauth_callback', allow_redirects=False)
    assert r.headers['location'] == './bgm.tv_auth'
    assert r.status_code == 307


def test_oauth_callback_success(client: TestClient):
    with aioresponses() as m:
        mock_bgm_auth_app(m)
        r = client.get(
            '/auth/api.v1/bgm.tv_oauth_callback',
            params={'code': 'query_code'},
            allow_redirects=False
        )
    assert r.status_code == 200, r.json()
