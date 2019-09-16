import re
from urllib import parse

import httpx
import peewee as pw
from pydantic import BaseModel

from app.log import logger
from app.client import http_client
from app.services import bgm_tv
from app.db_models import Ep, IqiyiBangumi, IqiyiEpisode
from app.video_website_spider.base import sync_db

from .base import BaseWebsite, UrlNotValidError


def get_ep_id_from_url(url: str):
    # 'http://www.iqiyi.com/v_19rro8bme0.html'
    url_obj: parse.ParseResult = parse.urlparse(url)
    return url_obj.path.split('/')[-1].replace('.html', '')


def get_bangumi_id_from_url(url: str):
    url_obj: parse.ParseResult = parse.urlparse(url)
    return url_obj.path.split('/')[-1].replace('.html', '')


class Iqiyi(BaseWebsite):
    bangumi_regex = re.compile(r'https?://www\.iqiyi\.com/(.*)\.html\??.*')
    episode_regex = re.compile(r'https?://www\.iqiyi\.com/(.*)\.html\??.*')

    alb_regex = re.compile(r'albumId: "([0-9]*)"')
    """only exists on album page"""

    album_name_regex = re.compile(r'albumName":"(.*?)","albumUrl')
    """exists on video page"""

    video_name_regex = re.compile(r',"shortTitle":"(.*?)","editorInfo')
    """exists on video page"""
    @classmethod
    def valid_ep_url(cls, url: str):
        if not cls.episode_regex.match(url):
            raise UrlNotValidError('https://www.iqiyi.com/{ep_id}.html')

    @classmethod
    def valid_subject_url(cls, url):
        if not cls.episode_regex.match(url):
            raise UrlNotValidError('https://www.iqiyi.com/{bangumi_id}.html')

    @classmethod
    @sync_db
    def subject(cls, subject_id: int, url: str):
        bangumi_id = get_bangumi_id_from_url(url)
        IqiyiBangumi.upsert(
            subject_id=subject_id,
            bangumi_id=bangumi_id,
        ).execute()

        album_id = http_client.get(url).text
        s = cls.alb_regex.search(album_id)
        if not s or not s.groups():
            logger.info("can't find albumId in {}", url)
            return

        album_id = s.groups()[0]
        r = httpx.get(
            'https://pcw-api.iqiyi.com/albums/album/avlistinfo',
            params={
                'aid': album_id,
                'page': 1,
                'size': 10000,
            },
            headers={
                'user-agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/74.0.3729.169 Safari/537.36'
                )
            }
        )
        list_info = r.json()
        if list_info['data'] == '参数错误':
            logger.error('参数错误 with album id {}', album_id)
            return
        else:
            eps = [ApiResult.parse_obj(x) for x in list_info['data']['epsodelist']]
        bgm_eps = bgm_tv.mirror.subject_eps(subject_id).eps
        bgm_ep_start = min(x.sort for x in bgm_eps)
        ep_start = min(x.order for x in eps)
        for ep in eps:
            for bgm_ep in bgm_eps:
                if (bgm_ep.sort - bgm_ep_start) == (ep.order - ep_start):
                    IqiyiEpisode.upsert(
                        ep_id=bgm_ep.id,
                        source_ep_id=ep.ep_id,
                        subject_id=subject_id,
                        title=ep.title,
                    ).execute()
                    break

    @classmethod
    @sync_db
    def ep(cls, ep_id: int, url: str):
        source_ep_id = get_ep_id_from_url(url)
        try:
            ep = Ep.get(ep_id=ep_id)
        except pw.DoesNotExist:
            return
        IqiyiEpisode.upsert(
            subject_id=ep.subject_id,
            ep_id=ep_id,
            source_ep_id=source_ep_id,
        ).execute()


class ApiResult(BaseModel):
    order: int
    playUrl: str
    shortTitle: str

    @property
    def ep_id(self):
        return self.playUrl.split('/')[3].replace('.html', '')

    @property
    def title(self):
        return self.shortTitle
