from fastapi import Header
from aioresponses import aioresponses
from starlette.testclient import TestClient

from app.db_models import sa
from app.api.auth.api_v1 import OAUTH_URL, get_current_user
from tests.mock_aiohttp.app import mock_bgm_auth_app


def test_oauth_redirect(client: TestClient):
    r = client.get("/auth/api.v1/bgm.tv_auth", allow_redirects=False)
    assert OAUTH_URL == r.headers["location"]
    assert r.status_code == 307


def test_oauth_callback_no_query_redirect(client: TestClient):
    r = client.get("/auth/api.v1/bgm.tv_oauth_callback", allow_redirects=False)
    assert r.headers["location"] == "./bgm.tv_auth"
    assert r.status_code == 307


def test_oauth_callback_no_query_code(client: TestClient):
    r = client.get("/auth/api.v1/bgm.tv_oauth_callback", allow_redirects=False)
    assert r.headers["location"] == "./bgm.tv_auth"
    assert r.status_code == 307


def test_oauth_callback_success(client: TestClient):
    with aioresponses() as m:
        mock_bgm_auth_app(m)
        r = client.get(
            "/auth/api.v1/bgm.tv_oauth_callback",
            params={"code": "query_code"},
            allow_redirects=False,
        )
    assert r.status_code == 200, r.json()


def test_oauth_refresh_token(client: TestClient):
    with aioresponses() as m:
        mock_bgm_auth_app(m, refresh_token="refresh token 233")

        async def mock_get_current_user(api_key=Header("api-key")):
            assert api_key == "user access token"
            return sa.UserToken(
                user_id=233,
                scope="",
                token_type="Bearer",
                expires_in=640000,
                auth_time=2333,
                access_token="access token example 1",
                refresh_token="refresh token 233",
                username="username",
                nickname="nickname",
                usergroup=10,
            )

        client.app.dependency_overrides[get_current_user] = mock_get_current_user

        r = client.post(
            "/auth/api.v1/bgm.tv_refresh",
            headers={"api-key": "user access token"},
            allow_redirects=False,
        )
    assert r.status_code == 200, r.json()
