import redis

import bgm_tv_spider.spiders.redis_bgm_tv
from bgm_tv_spider import settings

r = redis.Redis(host=settings.REDIS_HOST, db=0, **settings.REDIS_PARAMS)

r.lpush(
    settings.REDIS_START_URL_KEY,
    *(
        bgm_tv_spider.spiders.redis_bgm_tv.url_from_id(x)
        for x in range(1, 290000)
    )
)
