import urllib.parse

import parsel
import redis
import requests

import bgm_tv_spider.spiders.redis_bgm_tv
from bgm_tv_spider import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0
)

r = requests.get('http://mirror.bgm.rin.cat/wiki')

response = parsel.Selector(r.text)


def parse(response: parsel.Selector):
    links = set()
    for link in response.xpath('//*[@id="wikiEntryMainTab"]//li/a/@href'
                               ).extract():
        links.add(link)
    for link in response.xpath('//*[@id="latestEntryMainTab"]//li/a/@href'
                               ).extract():
        links.add(link)

    for link in links:
        if '/subject/' in link:
            url = urllib.parse.urljoin('http://mirror.bgm.rin.cat/wiki', link)
            print(url)
            redis_client.lpush(
                bgm_tv_spider.spiders.redis_bgm_tv.BgmTvSpider.redis_key,
                urllib.parse.urljoin('http://mirror.bgm.rin.cat/wiki', link)
            )


if __name__ == '__main__':
    parse(response)
