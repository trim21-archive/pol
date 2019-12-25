import asyncio
import urllib.parse

import aioredis
from lxml import etree

from app.client import http_client
from app.core.config import REDIS_URI, SPIDER_KEY


def generate_wiki_url():
    async def inner():
        print(generate_wiki_url.__qualname__, flush=True)
        redis_client = await aioredis.create_redis(REDIS_URI)
        r = http_client.get('https://mirror.bgm.rin.cat/wiki')
        await redis_client.lpush(SPIDER_KEY, *parse(r.text))

    asyncio.run(inner())


def parse(html: str):
    links = set()
    selector = etree.HTML(html)
    for link in selector.xpath('//*[@id="wikiEntryMainTab"]//li/a/@href'):
        links.add(link)
    for link in selector.xpath('//*[@id="latestEntryMainTab"]//li/a/@href'):
        links.add(link)
    print(len(links))
    for link in links:
        if '/subject/' in link:
            url = urllib.parse.urljoin('https://mirror.bgm.rin.cat/wiki', link)
            if url:
                yield url


if __name__ == '__main__':  # pragma: no cover
    generate_wiki_url()
