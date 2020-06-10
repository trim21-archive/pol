import pickle

import aioredis
from aioredis.commands import _NOTSET, Redis

from app.core import config


class PickleRedis(Redis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.script_hash = {}

    async def try_load_err_delete(self, key, value):
        try:
            return pickle.loads(value)
        except (ImportError, pickle.UnpicklingError):
            await self.delete(key=key)

    async def get(self, key, *, encoding=_NOTSET):
        r = await self.execute(b"GET", key, encoding=encoding)
        if r:
            try:
                return pickle.loads(r)
            except (ImportError, pickle.UnpicklingError, KeyError):
                await self.delete(key=key)

    async def set(self, key, value, *, expire=0, pexpire=0, exist=None):
        await super().set(
            key, pickle.dumps(value), expire=expire, pexpire=pexpire, exist=exist,
        )

    async def eval_script_by_name(self, script_name, keys=None, args=None):
        return await self.evalsha(
            self.script_hash[script_name], keys=keys or [], args=args or [],
        )

    async def get_session_and_extend_ttl(self, key, ttl):
        r = await self.eval_script_by_name(
            "get_session_and_extend_ttl.lua", keys=(key,), args=(ttl,),
        )
        if r:
            return await self.try_load_err_delete(key, r)


async def setup_redis_pool():
    pool: PickleRedis = await aioredis.create_redis_pool(
        config.REDIS_URI, minsize=5, maxsize=20, commands_factory=PickleRedis,
    )
    for lua_fs in (config.PROJ_ROOT / "app" / "lua").glob("*.lua"):
        with lua_fs.open("r") as f:
            content = f.read()
        script_hash = await pool.script_load(content)
        pool.script_hash[lua_fs.name] = script_hash

    return pool


async def create_redis_client():
    return await aioredis.create_redis_pool(config.REDIS_URI)
