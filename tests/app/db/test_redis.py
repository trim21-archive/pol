import pickle
import random
import string

import pytest

from app.core import config
from app.db.redis import PickleRedis, setup_redis_pool


def random_str(length: int = 8):
    all_char = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(all_char) for i in range(length))


async def close(r: PickleRedis):
    r.close()
    await r.wait_closed()


@pytest.mark.asyncio
async def test_setup_redis_pool():
    pool = await setup_redis_pool()
    assert isinstance(pool, PickleRedis)
    await close(pool)


@pytest.mark.asyncio
async def test_set_key(redis_client):
    pool = await setup_redis_pool()
    key = random_str()
    value = random_str()

    await pool.set(key, value)
    assert redis_client.get(key) == pickle.dumps(value), "redis value are not pickled"

    redis_client.delete(key)
    await close(pool)


@pytest.mark.asyncio
async def test_get_key(redis_client):
    pool = await setup_redis_pool()
    key = random_str()
    value = random_str()

    redis_client.set(key, pickle.dumps(value))
    assert value == await pool.get(key), "redis value are not pickled"
    redis_client.delete(key)
    await close(pool)


@pytest.mark.asyncio
async def test_decode_error(redis_client):
    pool = await setup_redis_pool()
    key = "unpickle-able key"
    value = "23333-123s"

    redis_client.set(key, value)
    value = await pool.get(key)
    assert value is None, "unpickle-able key should return `None`"
    assert not await pool.exists(key), "unpickle-able key should be deleted"

    redis_client.delete(key)
    await close(pool)


@pytest.mark.asyncio
async def test_redis_script_lua_name():
    pool = await setup_redis_pool()

    for lua_fs in (config.PROJ_ROOT / "app" / "lua").glob("*.lua"):
        assert lua_fs.name in pool.script_hash

    await close(pool)
