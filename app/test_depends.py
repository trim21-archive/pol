import httpx
import pytest

from app.depends import aio_http_client


@pytest.mark.asyncio
async def test_aio_http_client():
    client = await aio_http_client()
    assert isinstance(client, httpx.AsyncClient)
