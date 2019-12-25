import urllib.parse

import redis
import parsel

from app.client import http_client
from app.core.config import REDIS_HOST, SPIDER_KEY, REDIS_PASSWORD


def generate_wiki_url():
    print(generate_wiki_url.__qualname__, flush=True)
    redis_client = redis.Redis(
        host=REDIS_HOST,
        password=REDIS_PASSWORD,
    )

    r = http_client.get('https://mirror.bgm.rin.cat/wiki')

    response = parsel.Selector(r.text)
    redis_client.lpush(SPIDER_KEY, *parse(response))


def parse(response: parsel.Selector):
    links = set()
    for link in response.xpath('//*[@id="wikiEntryMainTab"]//li/a/@href').extract():
        links.add(link)
    for link in response.xpath('//*[@id="latestEntryMainTab"]//li/a/@href').extract():
        links.add(link)
    print(len(links))
    for link in links:
        if '/subject/' in link:
            url = urllib.parse.urljoin('https://mirror.bgm.rin.cat/wiki', link)
            if url:
                print(url)
                yield url


if __name__ == '__main__':  # pragma: no cover
    generate_wiki_url()
