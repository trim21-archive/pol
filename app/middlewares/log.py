import types
import traceback

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
                body = "".join(
                    traceback.format_exception(
                        type(exc),
                        exc,
                        exc.__traceback__,
                        limit=19 - len_tb(exc.__traceback__),
                    )
                )
                print(body)
                self.app.state.logger.exception(
                    "catch exception in middleware",
                    extra={
                        "body": body,
                        "url": self.get_url(scope),
                        "query": self.get_query(scope),
                        "headers": self.get_headers(scope),
                        "transaction": self.get_transaction(scope),
                        "event": "http.exception",
                        "exception": "{}.{}".format(
                            getattr(exc, "__module__", "builtin"),
                            exc.__class__.__name__,
                        ),
                    },
                )
            raise


def len_tb(tb: types.TracebackType):
    i = 1
    tb_next = tb.tb_next
    while tb_next is not None:
        tb_next = tb_next.tb_next
        i += 1
    return i
