import functools

import sentry_sdk

from .base import Middleware


class SentryMiddleware(Middleware):
    def __init__(self, app):
        super().__init__(app)

    async def __call__(self, scope, receive=None, send=None):
        async def __call__(self, scope, receive, send):
            hub = sentry_sdk.Hub.current
            with sentry_sdk.Hub(hub) as hub:
                with hub.configure_scope() as sentry_scope:
                    processor = functools.partial(
                        self.event_processor, asgi_scope=scope
                    )
                    sentry_scope.add_event_processor(processor)
                    try:
                        await self.app(scope, receive, send)
                    except Exception as exc:
                        hub.capture_exception(exc)
                        raise exc from None
