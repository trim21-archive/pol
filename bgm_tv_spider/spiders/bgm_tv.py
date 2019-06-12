import os
from typing import List
from collections import defaultdict

import peewee as pw
import scrapy.downloadermiddlewares.defaultheaders
from scrapy import Request

from bgm_tv_spider.items import EpItem, TagItem, SubjectItem, RelationItem
from bgm_tv_spider.models import Subject
from bgm_tv_spider.myTypes import TypeResponse, TypeSelectorList


def url_from_id(_id):
    return f'https://mirror.bgm.rin.cat/subject/{_id}'


blank_list = {'角色出演', '角色出演', '片头曲', '片尾曲', '其他'}
regexpNS = 'http://exslt.org/regular-expressions'

collector = {
    'wishes': 'wishes', 'done': 'collections', 'doings': 'doings',
    'on_hold': 'on_hole', 'dropped': 'dropped'
}


class BgmTvSpider(scrapy.Spider):
    name = 'bgm_tv'
    allowed_domains = ['mirror.bgm_tv_spider.rin.cat']
    start_urls = []

    def start_requests(self):
        start = int(os.getenv('SPIDER_START', '1'))
        end = os.getenv(
            'SPIDER_END',
            str(Subject.select(pw.fn.MAX(Subject.id)).scalar() + 2000),
        )
        end = int(end)
        if os.getenv('SPIDER_DONT_CACHE'):
            meta = {'dont_cache': True}
        else:
            meta = {}
        for i in range(start, end):
            yield Request(url_from_id(i), meta=meta)

    def parse(self, response: TypeResponse):
        subject_id = int(response.url.split('/')[-1])
        if '出错了' not in response.text:
            subject_item = SubjectItem()
            if '条目已锁定' in response.text:
                subject_item['id'] = subject_id
                subject_item['locked'] = True

            subject_type = response.xpath(
                '//*[@id="panelInterestWrapper"]//div[contains(@class, '
                '"global_score")]'
                '/div/small[contains(@class, "grey")]/text()'
            ).extract_first()

            subject_item['subject_type'] = subject_type.split()[1]
            if subject_item['subject_type'] == 'Anime':
                yield from get_ep_list(response, subject_id)
            subject_item['id'] = int(response.url.split('/')[-1])

            subject_item['info'] = get_info(response)
            subject_item['tags'] = 'tags'
            yield from get_tag_from_response(response, subject_id)
            subject_item['image'] = get_image(response)
            subject_item['score'] = get_score(response)
            subject_item['score_details'] = get_score_details(response)

            title = response.xpath('//*[@id="headerSubject"]/h1/a')[0]

            subject_item['name_cn'] = title.attrib['title']
            subject_item['name'] = title.xpath('text()').extract_first()

            # this will set 'wishes', 'done', 'doings', 'on_hold', 'dropped'
            subject_item.update(get_collector_count(response))

            for edge in get_relation(response, source=subject_item['id']):
                relation_item = RelationItem(**edge, )
                yield relation_item
                # yield Request(url_from_id(relation_item['target']))
            yield subject_item
        # else:
        #     self.logger.error('can\'t parse {}'.format(response.url))


def get_score_details(response: TypeResponse):
    detail = {
        'total': response
        .xpath('//*[@id="ChartWarpper"]/div/small/span/text()').extract_first()
    }
    for li in response.xpath(
        '//*[@id="ChartWarpper"]/ul[@class="horizontalChart"]/li'
    ):
        detail[li.xpath('.//span[@class="label"]/text()').extract_first()
               ] = li.xpath('.//span[@class="count"]/text()'
                            ).extract_first()[1:-1]
    return detail


def get_info(response: TypeResponse):
    info = defaultdict(list)

    for info_el in response.xpath('//*[@id="infobox"]/li'):
        info[info_el.xpath('span/text()').extract_first().replace(': ', '')
             ] = info_el.xpath('a/text()'
                               ).extract() or info_el.xpath('text()').extract()

    return dict(info)


def get_tag_from_response(response: TypeResponse, subject_id):
    for a in response.xpath(
        '//*[@id="subject_detail"]//div[@class="subject_tag_section"]'
        '/div[@class="inner"]/a'
    ):
        text = a.xpath('span/text()').extract_first()
        if not text:
            continue
        yield TagItem(
            subject_id=subject_id,
            text=text,
            count=int(a.xpath('small/text()').extract_first())
        )


def get_image(response: TypeResponse):
    not_nsfw_cover = response.xpath('//*[@id="bangumiInfo"]/div/div/a/img/@src')
    if not_nsfw_cover:
        return not_nsfw_cover.extract_first().replace(
            '//lain.bgm_tv_spider.tv/pic/cover/c/',
            'lain.bgm_tv_spider.tv/pic/cover/g/'
        )
    else:
        return 'lain.bgm_tv_spider.tv/img/no_icon_subject.png'


def get_score(response: TypeResponse):
    return response.xpath(
        '//*[@id="panelInterestWrapper"]//div[@class="global_score"]/span['
        '1]/text()'
    ).extract_first()


def get_collector_count(response: TypeResponse):
    item = {}
    for key, value in collector.items():
        item[key] = response.xpath(
            '//*[@id="subjectPanelCollect"]/span[@class="tip_i"]'
            '/a[re:test(@href, "{}$")]/text()'.format(value),
            namespaces={'re': regexpNS}
        ).extract_first()

    for key in collector:
        if item[key]:
            item[key] = int(item[key].split('人')[0])
        else:
            item[key] = 0
    return item


def get_relation(response: TypeResponse, source):
    section = response.xpath(
        '//div[@class="subject_section"][//h2[@class="subtitle" and contains('
        'text(), "关联条目")]]'
        '/div[@class="content_inner"]/ul/li'
    )
    relation = []
    chunk_list = []  # type:List[TypeSelectorList]

    for li in section:
        if 'sep' in li.attrib.get('class', ''):
            chunk_list.append([li])
        else:
            chunk_list[-1].append(li)
    for li_list in chunk_list:
        rel = li_list[0].xpath('span/text()').extract_first()
        for li in li_list:
            target = li.xpath('a/@href').extract_first()
            relation.append({
                'source': source,
                'target': int(target.split('/')[-1]),
                'relation': rel,
            })
    return relation


def get_ep_list(response: TypeResponse, subject_id: int):
    for ep in response.xpath(
        '//*[@id="subject_detail"]//ul[@class="prg_list"]/li/a'
    ):
        href = ep.attrib.get('href')
        if not href:
            continue
        ep_id = href.split('/')[-1]
        yield EpItem(
            subject_id=subject_id,
            ep_id=ep_id,
            name=ep.attrib.get('title', ''),
            episode=ep.xpath('./text()').extract_first() or '',
        )
