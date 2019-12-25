import copy

import redis

from app.core.config import REDIS_HOST, SPIDER_KEY, REDIS_PASSWORD


def chunk_iter_list(raw_list, chunk_size):
    ds = copy.copy(raw_list)
    while ds:
        yield ds[:chunk_size]
        ds = ds[chunk_size:]


def generate_full_url():
    print(generate_full_url.__qualname__, flush=True)
    r = redis.Redis(
        host=REDIS_HOST,
        password=REDIS_PASSWORD,
    )

    for chunk in chunk_iter_list(
        list(
            reversed([
                f'https://mirror.bgm.rin.cat/subject/{x}' for x in range(1, 300000)
            ])
        ),
        500,
    ):
        r.lpush(SPIDER_KEY, *chunk)


if __name__ == '__main__':  # pragma: no cover
    generate_full_url()
