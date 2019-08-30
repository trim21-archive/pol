import httpx

client = httpx.AsyncClient()


async def aio_http_client():
    return client
