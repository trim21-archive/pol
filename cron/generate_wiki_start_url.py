import urllib.parse

import parsel
import redis
import requests

from bgm_tv_spider import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST, db=0, **settings.REDIS_PARAMS
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
                settings.REDIS_START_URL_KEY,
                urllib.parse.urljoin('http://mirror.bgm.rin.cat/wiki', link)
            )


if __name__ == '__main__':
    parse(response)
