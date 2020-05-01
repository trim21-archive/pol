import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import ignore_logger

from app.core import config


def setup_sentry(app: FastAPI):
    if config.DSN:  # pragma: no cover
        ignore_logger("asyncio")
        sentry_sdk.init(
            dsn=config.DSN, release=config.COMMIT_SHA, integrations=[RedisIntegration()]
        )
        app.add_middleware(SentryAsgiMiddleware)
