import asyncio
from warnings import warn

import sentry_sdk
from fastapi import FastAPI
from sentry_asgi import SentryMiddleware

from app.api.api_v1.api import api_router
from app.core import config
from app.deprecation import bind_deprecated_path
from app.md2bbc import router as md2bbc_router

app = FastAPI(
    title='personal website',
    docs_url='/',
    redoc_url=None,
    openapi_url='/openapi.json',
    description='出于兴趣写的一些api，源码见'
    '[github](https://github.com/Trim21/personal-website)',
    version='0.0.1',
)
if config.DSN:
    sentry_sdk.init(dsn=config.DSN)
    app.add_middleware(SentryMiddleware)

bind_deprecated_path(app)
app.include_router(api_router, prefix='/api.v1')
app.include_router(md2bbc_router)
for router in app.routes:
    if router.path not in ['/', '/openapi.json']:
        if not asyncio.iscoroutinefunction(router.endpoint):
            warn(f'{router.path} is not async function')
