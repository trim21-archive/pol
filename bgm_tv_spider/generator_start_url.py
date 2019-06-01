import redis

import bgm_tv_spider.spiders.redis_bgm_tv
from bgm_tv_spider import settings

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

r.lpush(
    bgm_tv_spider.spiders.redis_bgm_tv.BgmTvSpider.redis_key,
    *(
        bgm_tv_spider.spiders.redis_bgm_tv.url_from_id(x)
        for x in range(1, 290000)
    )
)
