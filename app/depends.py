import httpx


async def aio_http_client():
    return httpx.AsyncClient()
