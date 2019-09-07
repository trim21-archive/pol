from app.log import logger
from app.middlewares.base import Middleware


class LogExceptionMiddleware(Middleware):
    def __init__(self, app):
        super().__init__(app)

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            logger.bind(
                url=self.get_url(scope),
                query=self.get_query(scope),
                headers=self.get_headers(scope),
                event='http.exception',
            ).exception('catch exception in middleware')
            raise exc from None
