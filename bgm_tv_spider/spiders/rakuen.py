import re
import unicodedata

import dateutil.parser
import lxml
import lxml.html
import scrapy
from parsel import Selector
from scrapy import Request

from bgm_tv_spider.items import ReplyItem, TopicItem
from bgm_tv_spider.myTypes import TypeResponse


class RakuenSpider(scrapy.Spider):
    name = 'rakuen'
    allowed_domains = ['mirror.bgm_tv_spider.rin.cat']
    start_urls = [
        # 'https://bgm.tv/rakuen/topiclist',
        'https://mirror.bgm.rin.cat/rakuen/topiclist?type=group',
        # 'https://bgm.tv/rakuen/topiclist?type=subject',
        # 'https://bgm.tv/rakuen/topiclist?type=ep',
        # 'https://bgm.tv/rakuen/topiclist?type=mono'
    ]

    def parse(self, response: TypeResponse):
        yield Request(
            'https://mirror.bgm.rin.cat/group/topic/350626',
            callback=self.parse_topic,
        )
        return
        for item in response.xpath('//*[@id="eden_tpc_list"]/ul/li'):
            url = item.xpath('./a/@href').extract_first().replace(
                '/rakuen/topic/group/', '/group/topic/'
            )
            yield Request(
                response.urljoin(url),
                callback=self.parse_topic,
            )

    def parse_topic(self, response: TypeResponse):
        topic = TopicItem()
        topic['last_reply'] = max(
            parse_datetime(x.xpath('./text()').extract_first())
            for x in response.xpath('//*[contains(@class,"re_info")]/small')
        )

        e = response.xpath('//*[contains(@class, "topic_content")]')
        post_topic = response.xpath('//*[contains(@class, "postTopic")]')
        topic['id'] = response.url.split('/')[-1]
        topic['content'] = parse_content(e)
        topic['group'] = response.xpath(
            '//*[@id="pageHeader"]/h1/span/a[1]/@href'
        ).extract_first().split('/')[-1]
        topic['title'] = response.xpath('//*[@id="pageHeader"]/h1/text()'
                                        ).extract_first()
        topic['author'] = post_topic.xpath(
            './div[contains(@class, "inner")]//a/@href'
        ).extract_first()
        if not topic['author']:
            raise KeyError('no author')
        else:
            topic['author'] = topic['author'].split('/')[-1]
        create_time = post_topic.xpath(
            './div[contains(@class, "re_info")]/small/text()'
        ).extract_first()
        topic['create_time'] = parse_datetime(create_time)

        comments = response.xpath('//*[@id="comment_list"]')
        last_reply = topic['create_time']
        for row in comments.xpath('./div[contains(@class, "row_reply")]'):
            for item in parse_row_reply(response, row, topic['id']):
                if item['create_time'] > last_reply:
                    last_reply = item['create_time']
                yield item
            # print(m_r)
        topic['last_reply'] = last_reply
        yield topic


def parse_row_reply(response: TypeResponse, row, topic_id):
    main_reply = ReplyItem()
    main_reply['reply_to'] = topic_id
    main_reply['id'] = row.xpath('./@id').extract_first().split('_')[-1]
    main_reply['author'] = row.xpath('./a[contains(@class, "avatar")]/@href'
                                     ).extract_first().split('/')[-1]
    main_reply['create_time'] = parse_datetime(
        row.xpath('./div[@class="re_info"]/small/text()').extract_first()
    )
    main_reply['content'] = parse_content(
        row.xpath('.//div[contains(@class, '
                  '"message")]')
    )
    # .extract_first()
    main_reply['topic_id'] = response.url.split('/')[-1]
    yield main_reply
    yield from parse_sub_reply(response, row, main_reply['id'])


def parse_sub_reply(response: TypeResponse, row, reply_to):
    for sub_reply_row in row.xpath('.//div[contains(@class, "sub_reply_bg")]'):
        sub_reply = ReplyItem()
        sub_reply['reply_to'] = reply_to
        sub_reply['id'] = sub_reply_row.xpath('./@id'
                                              ).extract_first().split('_')[-1]
        sub_reply['topic_id'] = response.url.split('/')[-1]
        sub_reply['author'] = sub_reply_row.xpath(
            './a[contains(@class, "avatar")]/@href'
        ).extract_first().split('/')[-1]
        sub_reply['create_time'] = parse_datetime(
            sub_reply_row.xpath('./div[@class="re_info"]/small/text()'
                                ).extract_first()
        )
        sub_reply['content'] = parse_content(
            sub_reply_row.xpath('.//div[contains(@class, "cmt_sub_content")]')
        )
        # .extract_first()
        yield sub_reply


def parse_datetime(time_string):
    if not time_string:
        return ''
    time_string = time_string.split('-', 1)[-1].strip()
    return dateutil.parser.parse(time_string)


bgm_face = re.compile(r'\(bgm_tv_spider\d+\)')
SPAN_BACK_MAP = {
    'bold': 'b',
    'italic': 'i',
    'underline': 'u',
    'through': 's',
}


def parse_content(node: Selector):
    s = ''
    for item in node.xpath('./node()'):
        if isinstance(item.root, str):
            s += item.root.strip()
        elif isinstance(item.root, lxml.html.HtmlElement):
            if item.root.tag == 'img':
                alt = item.root.attrib.get('alt', '')
                if bgm_face.match(alt):
                    s += alt
                    continue
            elif item.root.tag == 'div':
                s += unicodedata.normalize('NFKD',
                                           item.get().strip()).replace(
                                               '<br>\r\n', '\n'
                                           )
            else:
                s += item.get().strip()
            # continue
            # if item.root.tag == 'br':
            #     s += '\n'
            # elif item.root.tag == 'img':
            #     alt = item.root.attrib.get('alt', '')
            #     if bgm_face.match(alt):
            #         s += alt
            #         continue
            #     link = item.root.attrib.get('src')
            #     s += f'[img]{link}[/img]'
            # elif item.root.tag == 'a':
            #     href = (item.root.attrib['href'])
            #     text = (item.xpath('./text()').extract_first())
            #     if href == text:
            #         s += f'[url]{href}[/url]'
            #     else:
            #         s += f'[url={href}]{text}[/url]'
            # elif item.root.tag == 'span':
            #     text = item.xpath('./text()').extract_first()
            #     for key, value in SPAN_BACK_MAP.items():
            #         if key in item.root.attrib.get('style'):
            #             s += f'[{value}]{text}[/{value}]'
            #             break
            # else:
            #     raise ValueError(item.root.tag + ' is not impl ed yet')
    return s
