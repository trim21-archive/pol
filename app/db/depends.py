# Dependency
from starlette.requests import Request


async def get_db(request: Request):
    return request.app.state.objects


async def get_redis(request: Request):
    return request.app.state.redis_pool
