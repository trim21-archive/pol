import re
from typing import List

import peewee as pw
import requests
from pydantic import BaseModel

import app.video_website_spider.iqiyi
from app.log import logger
from app.db_models import (
    Ep, IqiyiBangumi, IqiyiEpisode, BilibiliBangumi, BilibiliEpisode
)
from app.db.database import db
from app.core.celery_app import celery
from app.video_website_spider.bilibili import get_initial_state_from_html


@celery.task(acks_late=True)
def test_celery(word: str):
    return f'test task return {word}'


alb_regex = re.compile(r'albumId: "([0-9]*)"')


@celery.task
def submit_bilibili_bangumi(subject_id: int, url: str):
    r = requests.get(url)
    initial_state = get_initial_state_from_html(r.text)
    if initial_state:
        initial_state = PlayerPageInitialState.parse_obj(initial_state)
    else:
        logger.error("can't get initial state from url %s", url)
        return

    with db.allow_sync():
        BilibiliBangumi.upsert(
            subject_id=subject_id,
            media_id=initial_state.mediaInfo.media_id,
            season_id=initial_state.mediaInfo.season_id,
        ).execute()


@celery.task
def submit_bilibili_ep(ep_id: int, url: str):
    """

    url would look like ``https://www.bilibili.com/bangumi/play/ep{ep_id}``
    and ep_id would by final source_ep_id

    Parameters
    ----------
    url:
        url of video player page
    ep_id:
        ep_id on bgm.tv

    Returns
    -------

    """
    r = requests.get(url)
    initial_state = get_initial_state_from_html(r.text)
    if initial_state:
        initial_state = PlayerPageInitialState.parse_obj(initial_state)
    else:
        logger.error("can't get initial state from url %s", url)
        return
    # source_ep_id = video_website_spider.bilibili.get_ep_id_from_url(url)

    with db.allow_sync():
        try:
            ep = Ep.get(ep_id=ep_id)
            BilibiliEpisode.upsert(
                ep_id=ep_id,
                source_ep_id=initial_state.epInfo.ep_id,
                subject_id=ep.subject_id,
            ).execute()
            logger.info(
                'upsert BilibiliEpisode with kwargs %r', {
                    'source_ep_id': ep_id,
                    'ep_id': initial_state.epInfo.ep_id,
                    'subject_id': ep.subject_id,
                }
            )
            BilibiliBangumi.get(subject_id=ep.subject_id)
        except Ep.DoesNotExist:
            logger.warning(
                'not fount episode %s with submit url %s', ep_id, url
            )
            return
        except BilibiliBangumi.DoesNotExist:
            BilibiliBangumi.upsert(
                media_id=initial_state.mediaInfo.media_id,
                season_id=initial_state.mediaInfo.season_id,
                subject_id=ep.subject_id,
            ).execute()


@celery.task
def submit_iqiyi_bangumi(subject_id: int, url: str):
    bangumi_id = app.video_website_spider.iqiyi.get_bangumi_id_from_url(url)

    with db.allow_sync():
        IqiyiBangumi.upsert(
            subject_id=subject_id,
            bangumi_id=bangumi_id,
        ).execute()

    # album_id = requests.get(url).text
    # s = alb_regex.search(album_id)
    # if not s or not s.groups():
    #     return
    #
    # album_id = s.groups()[0]
    # list_info = requests.get(
    #     'https://pcw-api.iqiyi.com/albums/album/avlistinfo',
    #     params={
    #         'aid': album_id,
    #         'page': 1,
    #         'size': 1000,
    #     }
    # ).json()
    # if list_info['data'] == '参数错误':
    #     return
    #
    # for ep in list_info['data']['epsodelist']:
    #     ep_id = ep['playUrl'].split('/')[3].replace(
    #         'v_',
    #         '',
    #     ).replace('.html', '')
    #     (
    #         ep['order'],
    #         {
    #             'site': 'iqiyi',
    #             'title': ep['name'],
    #             'url': ep['playUrl'],
    #             # 'http://www.iqiyi.com/v_19rro8bme0.html'
    #             'ep_id': ep_id,
    #         }
    #     )


@celery.task
def submit_iqiyi_ep(ep_id: int, url: str):
    source_ep_id = app.video_website_spider.iqiyi.get_ep_id_from_url(url)
    with db.allow_sync():
        try:
            ep = Ep.get(ep_id=ep_id)
        except pw.DoesNotExist:
            return
        IqiyiEpisode.upsert(
            subject_id=ep.subject_id,
            ep_id=ep_id,
            source_ep_id=source_ep_id,
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
