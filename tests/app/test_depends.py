import mock
import pytest
import asynctest.mock

from app.depends import aio_http_client


@pytest.mark.asyncio
async def test_aio_http_client():
    with mock.patch('httpx.AsyncClient') as mocker:
        m = mock.Mock()
        close = asynctest.mock.CoroutineMock()
        m.close = close
        mocker.return_value = m

        gen = aio_http_client()
        client = await gen.__anext__()
        assert client is m
        with pytest.raises(StopAsyncIteration):
            await gen.__anext__()

        close.assert_awaited_once()
