import httpx
import pytest
import starlette.requests

from app.depends import aio_http_client


@pytest.mark.asyncio
async def test_aio_http_client():
    req = starlette.requests.Request(scope={'type': 'http'})
    req.state.aio_client = httpx.AsyncClient()
    client = await aio_http_client(req)
    assert isinstance(client, httpx.AsyncClient)
    assert id(req.state.aio_client) == id(client)
