import httpx
import pytest
from fastapi import FastAPI

from app.middlewares.base import Middleware


@pytest.mark.asyncio
async def test_base():
    state = {'called': False}
    app = FastAPI()
    client = httpx.Client(app=app)

    class M(Middleware):
        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)
            assert self.get_url(scope) == 'http://example/openapi.json'
            assert self.get_transaction(
                scope
            ) == 'fastapi.applications.FastAPI.setup.<locals>.openapi', (
                'middleware transaction mismatch'
            )
            headers = self.get_headers(scope)
            assert headers['host'] == 'example', 'host mismatch'
            assert headers['user-agent'] == 'ua', 'user agent mismatch'
            assert self.get_query(scope) == 'q=1&w=2', 'middleware query mismatch'
            state['called'] = True

    app.add_middleware(M)

    await client.get(
        'http://example/openapi.json',
        headers={'user-agent': 'ua'},
        params={'q': 1, 'w': 2},
    )
    assert state['called'], 'middleware was not called'
