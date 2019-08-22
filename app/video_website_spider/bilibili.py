import re
import json
from typing import List
from urllib import parse

import requests
from pydantic import BaseModel

from app.log import logger
# class PlayerPageInitialState(BaseModel):
#     mediaInfo: MediaInfo
from app.service import bgm_tv
from app.db_models import Ep, BilibiliBangumi, BilibiliEpisode
from app.video_website_spider.base import sync_db

from .base import BaseWebsite, UrlNotValidError


def get_ep_id_from_url(url: str):
    url_obj: parse.ParseResult = parse.urlparse(url)
    return url_obj.path.split('/')[-1].repalce('ep', '')


def get_bangumi_id_from_url(url: str):
    url_obj: parse.ParseResult = parse.urlparse(url)
    return url_obj.path.split('/')[-1].repalce('ep', '')


regex = re.compile(
    r'<script>window\.'
    r'__INITIAL_STATE__=({.*});'
    r'\(function\(\){var s;\(s=document\.cu'
)


def get_initial_state_from_html(html: str) -> dict:
    x = regex.search(html)
    if x:
        json_text = x.group(1)
        if json_text:
            x = json.loads(json_text)
            return x


# class MediaInfo(BaseModel):
#     media_id: int
#     season_id: int


class Bilibili(BaseWebsite):
    bangumi_regex = re.compile(
        r'https?://www\.bilibili\.com/bangumi/media/md\d+/\??.*'
    )
    episode_regex = re.compile(
        r'https?://www\.bilibili\.com/bangumi/play/ep\d+\??.*'
    )

    @classmethod
    def valid_ep_url(cls, url: str):
        if not cls.episode_regex.match(url):
            raise UrlNotValidError(
                'https://www.bilibili.com/bangumi/play/ep{episode_id}'
            )

    @classmethod
    def valid_subject_url(cls, url):
        if not cls.episode_regex.match(url):
            raise UrlNotValidError(
                'https://www.bilibili.com/bangumi/media/md{media_id}'
            )

    @classmethod
    @sync_db
    def subject(cls, subject_id: int, url: str):
        r = requests.get(url)
        initial_state = get_initial_state_from_html(r.text)
        if initial_state:
            initial_state = PlayerPageInitialState.parse_obj(initial_state)
        else:
            logger.error("can't get initial state from url %s", url)
            return
        BilibiliBangumi.upsert(
            subject_id=subject_id,
            media_id=initial_state.mediaInfo.media_id,
            season_id=initial_state.mediaInfo.season_id,
        ).execute()
        bgm_eps = bgm_tv.server.subject_eps(subject_id).eps

        bgm_ep_start = min(x.sort for x in bgm_eps)
        ep_start = min(x.index for x in initial_state.epList)

        for ep in initial_state.epList:
            for bgm_ep in bgm_eps:
                if (bgm_ep.sort - bgm_ep_start) == (ep.index - ep_start):

                    BilibiliEpisode.upsert(
                        ep_id=bgm_ep.id,
                        source_ep_id=bgm_ep.id,
                        subject_id=subject_id,
                    ).execute()
                    break

    @classmethod
    @sync_db
    def ep(cls, ep_id: int, url: str):
        r = requests.get(url)
        initial_state = get_initial_state_from_html(r.text)
        if initial_state:
            initial_state = PlayerPageInitialState.parse_obj(initial_state)
        else:
            logger.error("can't get initial state from url %s", url)
            return
        # source_ep_id = video_website_spider.bilibili.get_ep_id_from_url(url)

        try:
            ep = Ep.get(ep_id=ep_id)
            BilibiliEpisode.upsert(
                ep_id=ep_id,
                source_ep_id=initial_state.epInfo.ep_id,
                subject_id=ep.subject_id,
            ).execute()
            logger.info(
                'upsert BilibiliEpisode with kwargs %r' % {
                    'source_ep_id': ep_id,
                    'ep_id': initial_state.epInfo.ep_id,
                    'subject_id': ep.subject_id,
                }
            )
        except Ep.DoesNotExist:
            logger.warning(
                'not fount episode %s with submit url %s', ep_id, url
            )
            return
        try:
            BilibiliBangumi.get(
                season_id=initial_state.mediaInfo.season_id,
                subject_id=ep.subject_id,
                media_id=initial_state.mediaInfo.media_id,
            )
            print('no exception')
        except BilibiliBangumi.DoesNotExist:
            logger.info(
                'upsert BilibiliBangumi<%r>' % {
                    'media_id': initial_state.mediaInfo.media_id,
                    'season_id': initial_state.mediaInfo.season_id,
                    'subject_id': ep.subject_id
                }
            )
            BilibiliBangumi.upsert(
                media_id=initial_state.mediaInfo.media_id,
                season_id=initial_state.mediaInfo.season_id,
                subject_id=ep.subject_id,
            ).execute()


class Param(BaseModel):
    season_id: str


class Result(BaseModel):
    param: Param
    media_id: int


class BiliBiliApiResult(BaseModel):
    code: int
    message: str
    result: Result


class PlayerPageMediaInfo(BaseModel):
    id: int
    """
    ``mediaInfo.media_id``
    """

    ssId: int
    """
    ``mediaInfo.season_id``
    """
    @property
    def media_id(self):
        return self.id

    @property
    def season_id(self):
        return self.ssId


class PlayerPageEpInfo(BaseModel):
    """
    schema of new player page
    don't have enough time to implement
    """
    id: int
    """
    ``epInfo.ep_id``
    """
    i: int
    """
    ``epInfo.index``
    """
    @property
    def ep_id(self):
        return self.id

    @property
    def index(self):
        return self.i + 1


class PlayerPageInitialState(BaseModel):
    mediaInfo: PlayerPageMediaInfo
    epInfo: PlayerPageEpInfo
    epList: List[PlayerPageEpInfo]
