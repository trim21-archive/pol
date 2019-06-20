from typing import List
from collections import defaultdict

from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from bgm_tv_spider import settings
from bgm_tv_spider.items import EpItem, TagItem, SubjectItem, RelationItem
from bgm_tv_spider.myTypes import TypeResponse, TypeSelectorList


def url_from_id(_id):
    return f'https://mirror.bgm.rin.cat/subject/{_id}'


blank_list = {'角色出演', '角色出演', '片头曲', '片尾曲', '其他'}
regexpNS = 'http://exslt.org/regular-expressions'

collector = {
    'wishes': 'wishes', 'done': 'collections', 'doings': 'doings',
    'on_hold': 'on_hole', 'dropped': 'dropped'
}


class BgmTvSpider(RedisSpider):
    name = 'redis_bgm_tv'
    allowed_domains = ['mirror.bgm.rin.cat']
    redis_key = settings.REDIS_START_URL_KEY
    redis_batch_size = 10

    def parse(self, response: TypeResponse):
        subject_id = int(response.url.split('/')[-1])
        if '502 Bad Gateway' in response.text:
            self.logger.warning(
                f'Retry request {subject_id} in a few seconds...'
            )
            if response.meta.get('delay_request'):
                self.logger.error(
                    '502 content, status: %s %s %s',
                    response.status,
                    response.meta,
                    response.url,
                )
            yield Request(
                url=response.url,
                meta={'dont_cache': True, 'delay_request': 5},
                dont_filter=True,
                callback=self.parse
            )
            return

        if '出错了' not in response.text:
            subject_item = SubjectItem()
            if '条目已锁定' in response.text:
                subject_item['id'] = subject_id
                subject_item['locked'] = True

            subject_type = response.xpath(
                '//*[@id="panelInterestWrapper"]'
                '//div[contains(@class,"global_score")]'
                '/div/small[contains(@class, "grey")]/text()'
            ).extract_first()
            if not subject_type:
                with open(
                    '.scrapy/debug/' + response.url.split('/')[-1] + '.html',
                    'w',
                    encoding='utf8'
                ) as f:
                    f.write(response.text)
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
            yield subject_item


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
            '//lain.bgm.tv/pic/cover/c/',
            'lain.bgm.tv/pic/cover/g/',
        )
    else:
        return 'lain.bgm.tv/img/no_icon_subject.png'


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
