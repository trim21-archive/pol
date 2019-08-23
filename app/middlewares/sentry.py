import sentry_sdk

from app.middlewares.base import Middleware


class SentryMiddleware(Middleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hub = sentry_sdk.Hub(sentry_sdk.Hub.current)

    async def __call__(self, scope, receive, send):
        with self.hub.configure_scope() as sentry_scope:
            sentry_scope.add_event_processor(
                lambda e, h: self.event_processor(e, h, scope)
            )
            try:
                await self.app(scope, receive, send)
            except Exception as exc:
                self.hub.capture_exception(exc)
                raise exc from None
