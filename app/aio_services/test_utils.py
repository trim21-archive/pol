from typing import Type

import httpx
import pytest

from app.aio_services.utils import ServerConnectionError, wrap_connection_error


@pytest.mark.asyncio
@pytest.mark.parametrize('exception', [httpx.Timeout, ConnectionError])
async def test_wrapper(exception: Type[Exception]):
    @wrap_connection_error
    async def exc():
        raise exception()

    with pytest.raises(ServerConnectionError):
        await exc()


@pytest.mark.asyncio
@pytest.mark.parametrize('exception', [ValueError, TypeError])
async def test_wrapper_not_catch_other_exception(exception: Type[Exception]):
    @wrap_connection_error
    async def exc():
        raise exception()

    with pytest.raises(exception):
        await exc()
