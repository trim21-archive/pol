import pickle

import pytest
from faker import Faker

from app.core import config
from app.db.redis import PickleRedis, setup_redis_pool


async def close(r: PickleRedis):
    r.close()
    await r.wait_closed()


@pytest.mark.asyncio
async def test_setup_redis_pool():
    pool = await setup_redis_pool()
    assert isinstance(pool, PickleRedis)
    await close(pool)


@pytest.mark.asyncio
async def test_set_key(redis_client, faker: Faker):
    pool = await setup_redis_pool()
    KEY = faker.name()
    VALUE = faker.name()

    await pool.set(KEY, VALUE)
    assert redis_client.get(KEY) == pickle.dumps(VALUE), 'redis value are not pickled'

    redis_client.delete(KEY)
    await close(pool)


@pytest.mark.asyncio
async def test_get_key(redis_client, faker: Faker):
    pool = await setup_redis_pool()
    KEY = faker.name()
    VALUE = faker.name()

    redis_client.set(KEY, pickle.dumps(VALUE))
    assert VALUE == await pool.get(KEY), 'redis value are not pickled'
    redis_client.delete(KEY)
    await close(pool)


@pytest.mark.asyncio
async def test_decode_error(redis_client, faker: Faker):
    pool = await setup_redis_pool()
    KEY = faker.name()
    VALUE = faker.name()

    redis_client.set(KEY, VALUE)
    await pool.get(KEY)
    assert not await pool.exists(KEY), 'un pickle-able key should be deleted'

    redis_client.delete(KEY)
    await close(pool)


@pytest.mark.asyncio
async def test_redis_script_lua_name():
    pool = await setup_redis_pool()

    for lua_fs in (config.PROJ_ROOT / 'app' / 'lua').glob('*.lua'):
        assert lua_fs.name in pool.script_hash

    await close(pool)
