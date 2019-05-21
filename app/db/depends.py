# Dependency
from starlette.requests import Request


def get_db(request: Request):
    return request.state.db


def get_redis(request: Request):
    return request.app.redis_pool
