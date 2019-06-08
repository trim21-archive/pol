# Dependency
from starlette.requests import Request

from app.db.database import objects


async def get_db(request: Request):
    return objects


async def get_redis(request: Request):
    return request.app.redis_pool
