import peewee as pw
from fastapi import Depends
from peewee_async import Manager
from starlette.status import HTTP_403_FORBIDDEN
from starlette.exceptions import HTTPException

from app.db.redis import PickleRedis
from app.db_models import UserToken
from app.db.depends import get_db, get_redis

from .scheme import API_KEY_HEADER, API_KEY_COOKIES
from .session import KEY_PREFIX, DEFAULT_TIMEOUT, SessionValue


async def get_api_key(
    api_key_header: str = Depends(API_KEY_HEADER),
    api_key_cookie: str = Depends(API_KEY_COOKIES),
) -> str:
    if api_key_header and api_key_cookie:
        if api_key_header != api_key_cookie:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=(
                    'try to auth with both http headers and cookies, '
                    'but different api_key'
                )
            )
    if api_key_cookie:
        return api_key_cookie
    elif api_key_header:
        return api_key_header
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail=(
            'You need to auth with api_key in header or cookies, '
            'see https://www.trim21.cn/#/auth for more details'
        )
    )


async def get_session(
    token: str = Depends(get_api_key),
    redis: PickleRedis = Depends(get_redis),
) -> SessionValue:
    token = token
    key = KEY_PREFIX + token
    r = await redis.get_session_and_extend_ttl(key, DEFAULT_TIMEOUT)
    if not r:
        raise HTTPException(403, 'api_key error or session expired')
    return r


async def get_current_user(
    session: SessionValue = Depends(get_session),
    db: Manager = Depends(get_db),
):
    try:
        return await db.get(UserToken, user_id=session.user_id)
    except pw.DoesNotExist:
        raise HTTPException(403)
