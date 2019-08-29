from better_exceptions import ExceptionFormatter

from app.log import logger
from app.middlewares.base import Middleware


class LogExceptionMiddleware(Middleware):
    def __init__(self, app):
        super().__init__(app)
        self.formatter = ExceptionFormatter(colored=False)
        # self.logger = logger.opt(raw=True)

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            event = self.event_processor({}, None, scope)
            logger.bind(
                url=self.get_url(scope),
                query=self.get_query(scope),
                headers=self.get_headers(scope),
                event=event,
            ).exception(
                self.formatter.format_exception(
                    type(exc),
                    exc,
                    exc.__traceback__,
                )
            )
            # print(exc)
            raise exc from None
