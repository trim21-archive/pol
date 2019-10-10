import mock
import httpx
import pytest
import asynctest.mock

from app.depends import aio_http_client


@pytest.mark.asyncio
async def test_aio_http_client():
    async with aio_http_client() as client:
        assert isinstance(client, httpx.AsyncClient)

    with mock.patch('httpx.AsyncClient') as mocker:
        m = mock.Mock()
        close = asynctest.mock.CoroutineMock()
        m.close = close
        mocker.return_value = m
        async with aio_http_client() as client:
            assert client is m
        close.assert_awaited_once()
