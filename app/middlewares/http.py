import time

import httpx
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from app.core import config


def setup_http_middleware(app: FastAPI):
    @app.middleware('http')
    async def async_http_client(request: Request, call_next):
        request.state.aio_client = httpx.AsyncClient(
            headers={'user-agent': config.REQUEST_SERVICE_USER_AGENT}
        )
        try:
            return await call_next(request)
        finally:
            await request.state.aio_client.close()

    @app.middleware('http')
    async def server_version_middleware(request: Request, call_next):
        response: Response = await call_next(request)
        response.headers['x-server-version'] = config.COMMIT_SHA
        return response

    @app.middleware('http')
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers['X-Process-Time'] = str(int(process_time * 1000)) + 'ms'
        return response
