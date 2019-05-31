import json

import scrapy.http
from scrapy.http import Request

from bgm_tv_spider.items import SubjectJsonItem
from bgm_tv_spider.models import Subject
from data_cleaner.main import SUBJECT_ID_END, SUBJECT_ID_START, chunk_iter_list


class BgmTvSubjectApiSpider(scrapy.Spider):
    name = 'bgm_tv_subject_api'
    allowed_domains = ['mirror.api.bgm_tv_spider.rin.cat']

    def start_requests(self):
        for chunk in chunk_iter_list(
            list(range(SUBJECT_ID_START, SUBJECT_ID_END)), 29000
        ):
            for i in Subject.select(
                Subject.id
            ).where((Subject.subject_type == 'Anime')
                    & (Subject.id.in_(chunk))):
                yield Request((
                    'https://mirror.api.bgm.rin.cat/subject/'
                    '{}?responseGroup=large'
                ).format(i.id))

    def parse(self, response: scrapy.http.Response):
        try:

            response_json = json.loads(response.text)
            if 'code' in response_json:
                return
            yield SubjectJsonItem(**response_json)  # , _id=response_json['id'])
        except json.decoder.JSONDecodeError:
            print(response.text)
