import urllib.parse

import redis
import parsel

from app.client import http_client
from bgm_tv_spider import settings


def generate_wiki_url():
    print(generate_wiki_url.__qualname__, flush=True)
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        **settings.REDIS_PARAMS,
    )

    r = http_client.get('https://mirror.bgm.rin.cat/wiki')

    response = parsel.Selector(r.text)
    redis_client.lpush(settings.REDIS_START_URL_KEY, *parse(response))


def parse(response: parsel.Selector):
    links = set()
    for link in response.xpath('//*[@id="wikiEntryMainTab"]//li/a/@href'
                               ).extract():
        links.add(link)
    for link in response.xpath('//*[@id="latestEntryMainTab"]//li/a/@href'
                               ).extract():
        links.add(link)
    print(len(links))
    for link in links:
        if '/subject/' in link:
            url = urllib.parse.urljoin('https://mirror.bgm.rin.cat/wiki', link)
            if url:
                print(url)
                yield url


if __name__ == '__main__':
    generate_wiki_url()
