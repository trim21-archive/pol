import copy
import asyncio

import aioredis

from app.core.config import REDIS_URI, SPIDER_KEY


def chunk_iter_list(raw_list, chunk_size):
    ds = copy.copy(raw_list)
    while ds:
        yield ds[:chunk_size]
        ds = ds[chunk_size:]


def generate_full_url():
    async def inner():
        print(generate_full_url.__qualname__, flush=True)
        r = await aioredis.create_redis(REDIS_URI)
        for chunk in chunk_iter_list(
            list(
                reversed([
                    f'https://mirror.bgm.rin.cat/subject/{x}' for x in range(1, 300000)
                ])
            ),
            500,
        ):
            await r.lpush(SPIDER_KEY, *chunk)

    asyncio.run(inner())


if __name__ == '__main__':  # pragma: no cover
    generate_full_url()
