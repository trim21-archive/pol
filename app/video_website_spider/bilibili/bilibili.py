import re
import json
from typing import Optional

import requests
from pydantic import ValidationError

from app.log import logger
from app.services import bgm_tv
from app.db_models import Ep, BilibiliBangumi, BilibiliEpisode
from app.video_website_spider.base import BaseWebsite, UrlNotValidError
from app.video_website_spider.bilibili.model import (
    PlayerPageInitialState, BangumiPageInitialState, BangumiPageMainSectionList
)

# def get_ep_id_from_url(url: str):
#     url_obj: parse.ParseResult = parse.urlparse(url)
#     return url_obj.path.split('/')[-1].repalce('ep', '')

# def get_bangumi_id_from_url(url: str):
#     url_obj: parse.ParseResult = parse.urlparse(url)
#     return url_obj.path.split('/')[-1].repalce('ep', '')

regex = re.compile(
    r'<script>window\.'
    r'__INITIAL_STATE__=({.*});'
    r'\(function\(\){var s;\(s=document\.cu'
)


def get_initial_state_from_html(html: str) -> Optional[dict]:
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
    bangumi_regex = re.compile(r'https?://www\.bilibili\.com/bangumi/media/md\d+/?.*')
    episode_regex = re.compile(r'https?://www\.bilibili\.com/bangumi/play/ep\d+/?.*')

    @classmethod
    def valid_ep_url(cls, url: str):
        if not cls.episode_regex.match(url):
            raise UrlNotValidError(
                'https://www.bilibili.com/bangumi/media/md{media_id} '
                'or https://www.bilibili.com/bangumi/play/ep{episode_id}'
            )

    @classmethod
    def valid_subject_url(cls, url):
        if not cls.bangumi_regex.match(url):
            if not cls.episode_regex.match(url):
                raise UrlNotValidError(
                    'https://www.bilibili.com/bangumi/media/md{media_id} '
                    'or https://www.bilibili.com/bangumi/play/ep{episode_id}'
                )

    @classmethod
    def subject(cls, subject_id: int, url: str):
        with requests.Session() as http_client:
            r = http_client.get(url)
            initial_state_dict = get_initial_state_from_html(r.text)

            if initial_state_dict:
                if 'ep' in url:
                    model = PlayerPageInitialState
                else:
                    model = BangumiPageInitialState
                try:
                    initial_state = model.parse_obj(initial_state_dict)
                except ValidationError as e:
                    print(initial_state['mainSectionList'])
                    logger.error(model.__name__)
                    logger.error(str(e))
                    logger.error(repr(initial_state))
                    return
            else:
                logger.error("can't get initial state from url {}", url)
                return

            if model == BangumiPageInitialState:
                section = http_client.get(
                    f'https://api.bilibili.com/pgc/web/'
                    f'season/section?season_id={initial_state.mediaInfo.season_id}'
                )

                initial_state.mainSectionList = BangumiPageMainSectionList.parse_obj(
                    section.json()['result']['main_section']
                )

            BilibiliBangumi.upsert(
                subject_id=subject_id,
                media_id=initial_state.mediaInfo.media_id,
                season_id=initial_state.mediaInfo.season_id
                or BilibiliBangumi.season_id.default,
                title=initial_state.mediaInfo.title,
            ).execute()
            bgm_eps = bgm_tv.mirror.subject_eps(subject_id).eps

            bgm_ep_start = min(x.sort for x in bgm_eps)
            ep_start = int(min(x.index for x in initial_state.epList))

            for bgm_ep in bgm_eps:
                for ep in initial_state.epList:
                    if not ep.index.isdecimal():
                        continue
                    if (bgm_ep.sort - bgm_ep_start) == (int(ep.index) - ep_start):

                        BilibiliEpisode.upsert(
                            ep_id=bgm_ep.id,
                            source_ep_id=ep.ep_id,
                            subject_id=subject_id,
                        ).execute()
                        break

    @classmethod
    def ep(cls, ep_id: int, url: str):
        with requests.Session() as http_client:
            r = http_client.get(url)
            initial_state_dict = get_initial_state_from_html(r.text)
            if initial_state_dict:
                initial_state = PlayerPageInitialState.parse_obj(initial_state_dict)
            else:
                logger.error("can't get initial state from url {}", url)
                return
            # source_ep_id = video_website_spider.bilibili.get_ep_id_from_url(url)

            try:
                ep = Ep.get(ep_id=ep_id)
                print(initial_state.epInfo.title)
                BilibiliEpisode.upsert(
                    ep_id=ep_id,
                    source_ep_id=initial_state.epInfo.ep_id,
                    subject_id=ep.subject_id,
                    title=initial_state.epInfo.title,
                ).execute()
                logger.info(
                    'upsert BilibiliEpisode with kwargs {{!r}}'.format(
                        source_ep_id=ep_id,
                        ep_id=initial_state.epInfo.ep_id,
                        subject_id=ep.subject_id,
                    )
                )
            except Ep.DoesNotExist:
                logger.warning('not fount episode {} with submit url {}', ep_id, url)
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
                    'upsert BilibiliBangumi<{!r}>', {
                        'media_id': initial_state.mediaInfo.media_id,
                        'season_id': initial_state.mediaInfo.season_id,
                        'subject_id': ep.subject_id
                    }
                )
                BilibiliBangumi.upsert(
                    media_id=initial_state.mediaInfo.media_id,
                    season_id=initial_state.mediaInfo.season_id,
                    subject_id=ep.subject_id,
                    title=initial_state.mediaInfo.title,
                ).execute()


if __name__ == '__main__':  # pragma: no cover
    Bilibili.subject(271724, 'https://www.bilibili.com/bangumi/media/md28221412')
