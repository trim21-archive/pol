import functools

from sentry_sdk import Hub
from sentry_sdk.tracing import Span
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware, _capture_exception


class SentryMiddleware(SentryAsgiMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def __call__(self, scope, receive=None, send=None):
        hub = Hub(Hub.current)
        with hub:
            with hub.configure_scope() as sentry_scope:
                sentry_scope.clear_breadcrumbs()
                sentry_scope._name = 'asgi'
                processor = functools.partial(self.event_processor, asgi_scope=scope)
                sentry_scope.add_event_processor(processor)

            if scope['type'] in ('http', 'websocket'):
                span = Span.continue_from_headers(dict(scope['headers']))
                span.op = '{}.server'.format(scope['type'])
            else:
                span = Span()
                span.op = 'asgi.server'

            span.set_tag('asgi.type', scope['type'])

            with hub.start_span(span) as span:
                try:
                    return await self.app(scope, receive, send)
                except Exception as exc:
                    _capture_exception(hub, exc)
                    raise exc from None
