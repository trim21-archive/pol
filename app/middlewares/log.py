from app.log import logger
from app.middlewares.base import Middleware


class LogExceptionMiddleware(Middleware):
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            event = self.event_processor({}, None, scope)
            logger.exception(
                exc,
                extra={
                    'url': self.get_url(scope),
                    'query': self.get_query(scope),
                    'headers': self.get_headers(scope),
                    'event': event,
                }
            )
            raise exc from None
