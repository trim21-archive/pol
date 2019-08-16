import os
import time
import asyncio
from logging import getLogger
from warnings import warn

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from app.api import bgm_tv, bgm_tv_auto_tracker
from app.log import setup_async_handler
from app.core import config
from app.md2bbc import router as md2bbc_router
from app.db.redis import setup_redis_pool
from app.db.database import objects
from app.deprecation import bind_deprecated_path
from app.api.api_v1.api import api_router
from app.middlewares.log import LogExceptionMiddleware

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
    from app.middlewares.sentry import SentryMiddleware
    import sentry_sdk
    from sentry_sdk.integrations.logging import ignore_logger
    ignore_logger('asyncio')
    sentry_sdk.init(dsn=config.DSN, release=config.COMMIT_SHA)
    app.add_middleware(SentryMiddleware)

app.add_middleware(LogExceptionMiddleware)
bind_deprecated_path(app)
app.include_router(api_router, prefix='/api.v1')
app.include_router(
    bgm_tv_auto_tracker.router,
    prefix='/bgm-tv-auto-tracker',
)
app.include_router(md2bbc_router)
app.include_router(bgm_tv.router, prefix='/bgm.tv', tags=['bgm.tv'])


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
async def startup():
    loop = asyncio.get_running_loop()
    await setup_async_handler(loop)

    app.objects = objects
    app.redis_pool = await setup_redis_pool()
    app.logger = getLogger('app')
    app.logger.info(
        f'server start at pid {os.getpid()}',
        extra={'event': 'startup', 'kwargs': {'pid': os.getpid()}}
    )


@app.on_event('shutdown')
async def shutdown():
    await objects.close()
    app.redis_pool.close()
