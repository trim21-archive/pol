import scrapy
from scrapy import Request

from bgm_tv_spider.myTypes import TypeResponse
from bgm_tv_spider.spiders import bgm_tv


class BgmTvWikiSpider(scrapy.Spider):
    name = 'bgm_tv_wiki'
    allowed_domains = ['mirror.bgm_tv_spider.rin.cat']
    start_urls = ['http://mirror.bgm.rin.cat/wiki']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, meta={'dont_cache': True})

    def parse(self, response: TypeResponse):

        links = set()
        for link in response.xpath('//*[@id="wikiEntryMainTab"]//li/a/@href'
                                   ).extract():
            links.add(link)
        for link in response.xpath('//*[@id="latestEntryMainTab"]//li/a/@href'
                                   ).extract():
            links.add(link)

        for link in links:
            if '/subject/' in link:
                yield Request(
                    response.urljoin(link),
                    callback=self.parse_page,
                    meta={'dont_cache': True}
                )

    parse_page = bgm_tv.BgmTvSpider.parse
