import asyncio
import functools

import httpx

from .exceptions import ServerConnectionError


def wrap_connection_error(func):
    assert asyncio.iscoroutinefunction(func), f'{func} is not coroutine function'

    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (httpx.Timeout, ServerConnectionError) as e:
            raise ServerConnectionError(raw_exception=e)

    return wrapped
