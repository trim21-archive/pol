import uuid

from fastapi import Depends
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from app.db.redis import PickleRedis
from app.db.depends import get_redis
from app.api.bgm_tv_auto_tracker.auth.scheme import cookie_scheme

KEY_PREFIX = 'personal-website:bgm-tv-auto-tracker:session:'

ANOTHER_KEY_PREFIX = 'pol:auth:session:'


class SessionValue(BaseModel):
    api_key: str
    user_id: int


async def get_session(
    token: str = Depends(cookie_scheme),
    redis: PickleRedis = Depends(get_redis),
) -> SessionValue:
    r = await redis.get(KEY_PREFIX + token)
    if not r:
        r = await redis.get(ANOTHER_KEY_PREFIX + token)
        if not r:
            raise HTTPException(403, 'you need to auth your bgm.tv account first')
    return r


async def new_session(
    user_id,
    redis: PickleRedis,
) -> SessionValue:
    token = generator_session_id()
    session = SessionValue(api_key=token, user_id=user_id)
    await redis.set(
        ANOTHER_KEY_PREFIX + token,
        session,
        expire=60 * 60 * 24 * 30,
    )
    return session


def generator_session_id():
    return uuid.uuid4().hex
