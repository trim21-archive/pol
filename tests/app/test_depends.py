from contextlib import asynccontextmanager

import mock
import httpx
import pytest
import asynctest.mock

from app.depends import aio_http_client


@pytest.mark.asyncio
async def test_aio_http_client():
    # todo: need a way to test yield style depends without context manager
    async_ctx_manager = asynccontextmanager(aio_http_client)
    async with async_ctx_manager() as client:
        assert isinstance(client, httpx.AsyncClient)

    with mock.patch('httpx.AsyncClient') as mocker:
        m = mock.Mock()
        close = asynctest.mock.CoroutineMock()
        m.close = close
        mocker.return_value = m
        async with async_ctx_manager() as client:
            assert client is m
        close.assert_awaited_once()
