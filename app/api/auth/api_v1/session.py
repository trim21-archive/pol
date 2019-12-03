import uuid
import hashlib

from pydantic import BaseModel

from app.db.redis import PickleRedis

KEY_PREFIX = 'pol:server:session:'
DEFAULT_TIMEOUT = 30 * 7 * 24 * 3600


class SessionValue(BaseModel):
    api_key: str
    user_id: int


async def new_session(user_id: int, redis: PickleRedis) -> SessionValue:
    token = generator_session_id(user_id)
    session = SessionValue(api_key=token, user_id=user_id)
    await redis.set(
        KEY_PREFIX + token,
        session,
        expire=DEFAULT_TIMEOUT,
    )
    return session


def generator_session_id(user_id):
    h = hashlib.sha256()
    h.update(str(user_id).encode())

    return h.hexdigest()[:16] + uuid.uuid4().hex[:32]


if __name__ == '__main__':

    def t():
        print(len(uuid.uuid4().hex[:32]))

    t()
