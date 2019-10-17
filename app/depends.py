import httpx

from app.core import config


async def aio_http_client() -> httpx.AsyncClient:
    aio_client = httpx.AsyncClient(
        headers={'user-agent': config.REQUEST_SERVICE_USER_AGENT}
    )
    try:
        yield aio_client
    finally:
        await aio_client.close()
