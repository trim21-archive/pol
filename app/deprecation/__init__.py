from fastapi import FastAPI

from .make_ics import router


def bind_deprecated_path(app: FastAPI):
    app.include_router(router)
