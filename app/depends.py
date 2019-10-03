import httpx
from starlette.requests import Request


async def aio_http_client(request: Request) -> httpx.AsyncClient:
    return request.state.aio_client
