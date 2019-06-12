import time
import asyncio
from warnings import warn

import sentry_sdk
from fastapi import FastAPI
from sentry_asgi import SentryMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api import bgm_tv_auto_tracker
from app.core import config
from app.md2bbc import router as md2bbc_router
from app.db.redis import setup_redis_pool
from app.db.database import objects
from app.deprecation import bind_deprecated_path
from app.api.api_v1.api import api_router

app = FastAPI(
    title='personal website',
    docs_url='/',
    redoc_url=None,
    openapi_url='/openapi.json',
    description='出于兴趣写的一些api，源码见'
    '[GitHub](https://github.com/Trim21/personal-website)\n'
    f'当前版本[{config.COMMIT_SHA}]'
    f'(https://github.com/Trim21/personal-website/tree/{config.COMMIT_SHA})',
    version='0.0.1',
)
if config.DSN:
    sentry_sdk.init(dsn=config.DSN)
    app.add_middleware(SentryMiddleware)
bind_deprecated_path(app)
app.include_router(api_router, prefix='/api.v1')
app.include_router(
    bgm_tv_auto_tracker.router,
    prefix='/bgm-tv-auto-tracker',
    tags=['bgm-tv-auto-tracker'],
)
app.include_router(md2bbc_router)


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


for router in app.routes:
    if not asyncio.iscoroutinefunction(router.endpoint):
        warn(f'{router.path} {router.endpoint} is not async function')


@app.on_event('startup')
async def setup():
    app.objects = objects
    app.redis_pool = await setup_redis_pool()


@app.on_event('shutdown')
async def shutdown():
    await objects.close()
    app.redis_pool.close()
