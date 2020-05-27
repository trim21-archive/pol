from loguru import logger

from app.core import config

if config.DSN:  # pragma: no cover
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration

    logger.debug("setup sentry for celery")
    sentry_sdk.init(
        dsn=config.DSN, release=config.COMMIT_SHA, integrations=[CeleryIntegration()],
    )
