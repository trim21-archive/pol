import os
import threading

import jinja2
from fastapi import FastAPI

from app.api import auth, bgm_tv, bgm_tv_auto_tracker
from app.log import logger
from app.core import config
from app.md2bbc import router as md2bbc_router
from app.db.redis import setup_redis_pool
from app.db.database import objects
from app.deprecation import bind_deprecated_path
from app.api.api_v1.api import api_router
from app.middlewares.log import LogExceptionMiddleware
from app.middlewares.http import setup_http_middleware

template = jinja2.Template(
    """出于兴趣写的一些api，源码见[GitHub](https://github.com/Trim21/pol)

当前版本[{{config.COMMIT_REV}}](https://github.com/Trim21/pol/tree/{{config.COMMIT_REV}})

更详细的文档见 [github pages](https://trim21.github.io/pol/)
"""
)

app = FastAPI(
    debug=config.DEBUG,
    title=config.APP_NAME,
    version=config.COMMIT_REV,
    docs_url='/',
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None,
    openapi_url='/openapi.json',
    description=template.render(config=config),
)

if config.DSN:  # pragma: no cover
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

setup_http_middleware(app)
app.add_middleware(LogExceptionMiddleware)
app.include_router(auth.router, prefix='/auth', tags=['auth'])
bind_deprecated_path(app)
app.include_router(api_router, prefix='/api.v1')
app.include_router(bgm_tv_auto_tracker.router, prefix='/bgm-tv-auto-tracker')
app.include_router(md2bbc_router)
app.include_router(bgm_tv.router, prefix='/bgm.tv', tags=['bgm.tv'])


@app.on_event('startup')
async def startup():
    app.state.objects = objects
    app.state.redis_pool = await setup_redis_pool()
    app.state.logger = logger
    app.state.logger.bind(
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
    app.state.redis_pool.close()
    await app.state.redis_pool.wait_closed()
