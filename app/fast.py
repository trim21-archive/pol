import os
import time
import threading

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from app.api import auth, bgm_tv, bgm_tv_auto_tracker
from app.log import logger
from app.core import config
from app.md2bbc import router as md2bbc_router
from app.db.redis import setup_redis_pool
from app.db.database import objects
from app.deprecation import bind_deprecated_path
from app.api.api_v1.api import api_router
from app.middlewares.log import LogExceptionMiddleware

app = FastAPI(
    debug=config.DEBUG,
    title=config.APP_NAME,
    version=config.COMMIT_REV,
    docs_url='/',
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
    openapi_url='/openapi.json',
    description=(
        '出于兴趣写的一些api，源码见'
        '[GitHub](https://github.com/Trim21/pol)\n'
        f'当前版本[{config.COMMIT_REV}]'
        f'(https://github.com/Trim21/pol/tree/{config.COMMIT_REV})\n\n'
        '更详细的文档见 [github pages](https://trim21.github.io/pol/)'
    ),
)

if config.DSN:
    import sentry_sdk
    from sentry_sdk.integrations.logging import ignore_logger
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

    ignore_logger('asyncio')
    logger.debug('setup sentry')
    sentry_sdk.init(
        dsn=config.DSN, release=config.COMMIT_SHA, integrations=[RedisIntegration()]
    )
    app.add_middleware(SentryAsgiMiddleware)

app.add_middleware(LogExceptionMiddleware)
app.include_router(auth.router, prefix='/auth', tags=['auth'])
bind_deprecated_path(app)
app.include_router(api_router, prefix='/api.v1')
app.include_router(bgm_tv_auto_tracker.router, prefix='/bgm-tv-auto-tracker')
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


@app.on_event('startup')
async def startup():
    app.objects = objects
    app.redis_pool = await setup_redis_pool()
    app.logger = logger
    app.logger.bind(
        event='startup',
        kwargs={
            'pid': os.getpid(),
            'thread': threading.get_ident(),
        },
    ).info(
        'server start at pid {}, tid {}',
        os.getpid(),
        threading.get_ident(),
    )


@app.on_event('shutdown')
async def shutdown():
    await objects.close()
    app.redis_pool.close()
