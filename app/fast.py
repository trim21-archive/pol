import asyncio
from warnings import warn

import sentry_sdk
from fastapi import FastAPI
from sentry_asgi import SentryMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api.api_v1.api import api_router
from app.core import config
from app.db.database import objects
from app.db.redis import setup_redis_pool
from app.deprecation import bind_deprecated_path
from app.md2bbc import router as md2bbc_router

app = FastAPI(
    title='personal website',
    docs_url='/',
    redoc_url=None,
    openapi_url='/openapi.json',
    description='出于兴趣写的一些api，源码见'
    '[github](https://github.com/Trim21/personal-website)\n\n'
    f'当前版本[{config.COMMIT_SHA}](https://github.com/Trim21/personal-website/tree/{config.COMMIT_SHA})',
    version='0.0.1',
)
if config.DSN:
    sentry_sdk.init(dsn=config.DSN)
    app.add_middleware(SentryMiddleware)

bind_deprecated_path(app)
app.include_router(api_router, prefix='/api.v1')
app.include_router(md2bbc_router)


@app.middleware('http')
async def db_session_middleware(request: Request, call_next):
    request.state.db = objects
    return await call_next(request)


@app.middleware('http')
async def server_version_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers['x-server-version'] = config.COMMIT_SHA
    return response


for router in app.routes:
    if router.path not in ['/', '/openapi.json']:
        if not asyncio.iscoroutinefunction(router.endpoint):
            warn(f'{router.path} is not async function')


@app.on_event('startup')
async def setup():
    app.redis_pool = await setup_redis_pool()