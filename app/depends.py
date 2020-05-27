import aiohttp
from fastapi import Depends, FastAPI
from aiologger import Logger
from starlette.requests import Request


async def fastapi_app(request: Request) -> FastAPI:
    return request.app


async def aiohttp_session(app: FastAPI = Depends(fastapi_app)) -> aiohttp.ClientSession:
    return app.state.client_session


async def get_logger(app: FastAPI = Depends(fastapi_app)) -> Logger:
    return app.state.logger
