# Dependency
from starlette.requests import Request


def get_db(request: Request):
    return request.app.objects


def get_redis(request: Request):
    return request.app.redis_pool
