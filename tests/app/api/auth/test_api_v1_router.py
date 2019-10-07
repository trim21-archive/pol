import datetime

import httpx
from fastapi import Form, FastAPI
from fastapi.params import Header
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from app.depends import aio_http_client
from app.api.auth.api_v1 import OAUTH_URL
from app.services.bgm_tv.model import UserInfo, AuthResponse


def mock_http_client(app):
    async def c():
        return httpx.AsyncClient(app=app)

    return c


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
    client.app.dependency_overrides[aio_http_client] = mock_http_client(
        get_mock_bgm_auth_app()
    )
    r = client.get(
        '/auth/api.v1/bgm.tv_oauth_callback',
        params={'code': 'query_code'},
        allow_redirects=False
    )
    assert r.status_code == 200


def get_mock_bgm_auth_app():
    app = FastAPI()

    @app.post('/oauth/access_token')
    async def access_token(
        code: str = Form(...),
        client_id: str = Form(...),
        grant_type: str = Form(...),
        client_secret: str = Form(...),
        redirect_uri: str = Form(...),
        host: str = Header(...),
    ):
        assert host == 'bgm.tv'
        return JSONResponse(
            AuthResponse(
                access_token='access_token_example',
                expires_in=68400,
                token_type='access_token',
                scope=None,
                user_id=233,
                refresh_token='refresh_token_example'
            ).dict(),
            headers={'Date': datetime.datetime.now().isoformat()},
        )

    @app.get('/user/{user_id}')
    async def user_info(
        user_id: str,
        host: str = Header(...),
    ):
        assert host == 'mirror.api.bgm.rin.cat'
        return UserInfo(
            id=2333,
            url=f'http://bgm.tv/user/{user_id}',
            username=user_id,
            nickname='nickname',
            avatar={
                'large': 'http://lain.bgm.tv/pic/user/l/000/28/76/287622.jpg',
                'medium': 'http://lain.bgm.tv/pic/user/m/000/28/76/287622.jpg',
                'small': 'http://lain.bgm.tv/pic/user/s/000/28/76/287622.jpg?'
            },
            sign='hehe',
            usergroup=10
        )

    return app
