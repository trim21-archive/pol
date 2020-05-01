import json
import asyncio
import platform

from better_exceptions import THEME, CAP_CHAR, PIPE_CHAR, ExceptionFormatter
from aiologger.loggers.json import JsonLogger, ExtendedLogRecord
from aiologger.handlers.base import Handler

from app.core import config


class RedisHandler(Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formatter = ExceptionFormatter(
            colored=False,
            theme=THEME,
            max_length=None,
            pipe_char=PIPE_CHAR,
            cap_char=CAP_CHAR,
        )

    async def emit(self, record: ExtendedLogRecord) -> None:
        print(self.format(record))

    async def close(self) -> None:
        pass

    @staticmethod
    def format(record: ExtendedLogRecord):
        if record.exc_info:
            print(record.exc_text)
        # o = deepcopy(extra)
        # o.update(
        o = {
            "@metadata": {"beat": "py_logging", "version": config.COMMIT_REF},
            "version": config.COMMIT_REF,
            "platform": platform.platform(),
            "msg": record.get_message(),
            "logged_at": record.created,
            "line_number": record.lineno,
            "function": record.funcName,
            "level": record.levelname,
            "module": record.module,
            "process": record.process,
        }
        o.update(record.extra)
        return json.dumps(o)


async def main():
    logger = JsonLogger(name="pol")
    logger.add_handler(RedisHandler())
    formatter = ExceptionFormatter(
        colored=False,
        theme=THEME,
        max_length=None,
        pipe_char=PIPE_CHAR,
        cap_char=CAP_CHAR,
    )
    logger.info("Function, file path and line number wont be printed")
    try:
        a = 1
        b = 0
        a / b
    except ZeroDivisionError as e:
        body = formatter.format_exception(ZeroDivisionError, e, e.__traceback__)
        logger.exception(
            "exception",
            extra={
                "body": body,
                "event": "http.exception",
                "exception": "{}.{}".format(
                    getattr(e, "__module__", "builtin"), e.__class__.__name__,
                ),
            },
        )

    await logger.shutdown()


loop = asyncio.ProactorEventLoop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
loop.close()
