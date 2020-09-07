import time
import types
import traceback

from fastapi import FastAPI
from starlette.requests import Request

from app.core import config


def setup_http_middleware(app: FastAPI):
    @app.middleware("http")
    async def add_extra_headers(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(int(process_time * 1000)) + "ms"
        response.headers["x-server-version"] = config.COMMIT_REF
        return response

    @app.middleware("http")
    async def log(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            body = "".join(
                traceback.format_exception(
                    type(exc),
                    exc,
                    exc.__traceback__,
                    limit=19 - len_tb(exc.__traceback__),
                )
            )
            app.state.logger.exception(
                "catch exception in middleware",
                extra={
                    "body": body,
                    "url": str(request.url),
                    "query": dict(request.query_params),
                    "x-request-id": request.headers.get("x-request-id", ""),
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
