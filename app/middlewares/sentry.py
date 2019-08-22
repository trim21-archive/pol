import functools

import sentry_sdk

from app.middlewares.base import Middleware


class SentryMiddleware(Middleware):
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

    def event_processor(self, event, hint, asgi_scope):
        if asgi_scope['type'] in ('http', 'websocket'):
            event['request'] = {
                'url': self.get_url(asgi_scope),
                'method': asgi_scope['method'],
                'headers': self.get_headers(asgi_scope),
                'query_string': self.get_query(asgi_scope),
            }
        if asgi_scope.get('client'):
            event['request']['env'] = {'REMOTE_ADDR': asgi_scope['client'][0]}
        if asgi_scope.get('endpoint'):
            event['transaction'] = self.get_transaction(asgi_scope)
        return event
