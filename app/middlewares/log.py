from app.log import logger
from app.middlewares.base import Middleware


class LogExceptionMiddleware(Middleware):
    def __init__(self, app):
        super().__init__(app)
        self.scope_types = ("http", "websocket")

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            if scope["type"] in self.scope_types:
                logger.bind(
                    url=self.get_url(scope),
                    query=self.get_query(scope),
                    headers=self.get_headers(scope),
                    transaction=self.get_transaction(scope),
                    event="http.exception",
                    exception="{}.{}".format(
                        getattr(exc, "__module__", "builtin"), exc.__class__.__name__,
                    ),
                ).exception("catch exception in middleware")
            raise exc from None
