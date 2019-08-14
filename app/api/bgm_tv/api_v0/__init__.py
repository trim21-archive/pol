import re
import enum
from typing import List, Union

from fastapi import Depends, APIRouter
from pydantic import BaseModel
from peewee_async import Manager
from pydantic.types import UrlStr
from starlette.exceptions import HTTPException

from app.core import config
from app.worker import (
    submit_iqiyi_ep, submit_bilibili_ep, submit_iqiyi_bangumi,
    submit_bilibili_bangumi
)
from app.db_models import (
    IqiyiBangumi, IqiyiEpisode, BilibiliBangumi, BilibiliEpisode
)
from app.db.depends import get_db

router = APIRouter()


class SupportWebsite(str, enum.Enum):
    bilibili = 'bilibili'
    iqiyi = 'iqiyi'


class PlayerEpisode(BaseModel):
    subject_id: int
    source_ep_id: str
    website: SupportWebsite


class PlayerSubject(BaseModel):
    website: SupportWebsite
    url: str
    bangumi_id: str


class SubmitBody(BaseModel):
    website: SupportWebsite
    url: UrlStr


@router.get(
    '/player/subject/{subject_id}',
    description='**unstable** \n\n '
    '针对bgm.tv的单集获取视频网站播放地址.\n\n'
    '数据的有效性依赖于大家共同的维护, 请同时实现<!-- 报错和 -->提交播放地址的功能',
    response_model=List[PlayerSubject],
    include_in_schema=config.DEBUG,
)
async def get_player_url_of_subject(
    subject_id: int,
    db: Manager = Depends(get_db),
):
    return [{
        'website': x.name,
        'bangumi_id': x.bangumi_id,
        'url': x.url,
    } for x in await get_all_bangumi_of_subject(db, subject_id)]


@router.get(
    '/player/ep/{ep_id}',
    description='**unstable** \n\n '
    '针对bgm.tv的单集获取视频网站播放地址.\n\n'
    '数据的有效性依赖于大家共同的维护, 请同时实现<!-- 报错和 -->提交播放地址的功能',
    response_model=List[PlayerEpisode],
    include_in_schema=config.DEBUG,
)
async def get_player_url_of_episode(
    ep_id: int,
    db: Manager = Depends(get_db),
):
    return [{
        'website': x.name,
        'url': x.url,
        'subject_id': x.subject_id,
    } for x in await get_all_episode_player(db, ep_id)]


bilibili_bangumi = re.compile(
    r'https?://www\.bilibili\.com/bangumi/media/md\d+/\??.*'
)
bilibili_episode = re.compile(
    r'https?://www\.bilibili\.com/bangumi/play/ep\d+\??.*'
)
iqiyi_bangumi = re.compile(r'https?://www\.iqiyi\.com/a_(.*)\.html\??.*')
iqiyi_episode = re.compile(r'https?://www\.iqiyi\.com/v_(.*)\.html\??.*')


@router.post(
    '/player/subject/{subject_id}',
    description='**unstable** \n\n '
    '针对bgm.tv的单集获取视频网站播放地址.\n\n'
    '数据的有效性依赖于大家共同的维护, 请同时实现<!-- 报错和 -->提交播放地址的功能',
    response_model=List[PlayerSubject],
    include_in_schema=config.DEBUG,
)
async def submit_player_url_of_subject(
    subject_id: int,
    submit: SubmitBody,
):
    if submit.website == SupportWebsite.bilibili:
        if not bilibili_bangumi.match(submit.url):
            raise HTTPException(
                422, 'url not correct, should match ' + bilibili_bangumi.pattern
            )
        submit_bilibili_bangumi.delay(
            subject_id=subject_id,
            url=submit.url,
        )
    elif submit.website == SupportWebsite.iqiyi:
        if not iqiyi_bangumi.match(submit.url):
            raise HTTPException(
                422, 'url not correct, should match ' + iqiyi_bangumi.pattern
            )
        submit_iqiyi_bangumi.delay(
            subject_id=subject_id,
            url=submit.url,
        )


@router.post(
    '/player/ep/{ep_id}',
    description='**unstable** \n\n '
    '针对bgm.tv的单集获取视频网站播放地址.\n\n',
    response_model=List[PlayerEpisode],
    include_in_schema=config.DEBUG,
)
async def submit_player_url_for_episode(
    ep_id: int,
    submit: SubmitBody,
):
    if submit.website not in submit.url:
        raise HTTPException(422, detail='url mismatch with website')
    if submit.website == SupportWebsite.bilibili:
        if not bilibili_episode.match(submit.url):
            raise HTTPException(
                422, 'url not correct, should match ' + str(bilibili_episode)
            )
        submit_bilibili_ep.delay(
            ep_id=ep_id,
            url=submit.url,
        )
    elif submit.website == SupportWebsite.iqiyi:
        if not iqiyi_episode.match(submit.url):
            raise HTTPException(
                422, 'url not correct, should match ' + iqiyi_episode.pattern
            )

        submit_iqiyi_ep.delay(
            ep_id=ep_id,
            url=submit.url,
        )


async def get_all_bangumi_of_subject(
    db: Manager, subject_id
) -> List[Union[BilibiliBangumi, IqiyiBangumi]]:
    bangumi_list = []
    for model in (BilibiliBangumi, IqiyiBangumi):
        try:
            bangumi_list.append(await db.get(model, subject_id=subject_id))
        except model.DoesNotExist:
            pass
    return bangumi_list


async def get_all_episode_player(
    db: Manager, ep_id
) -> List[Union[BilibiliEpisode, IqiyiEpisode]]:
    episodes = []
    for model in (BilibiliEpisode, IqiyiEpisode):
        try:
            episodes.append(await db.get(model, ep_id=ep_id))
        except model.DoesNotExist:
            pass
    return episodes


def parse_url_to_website():
    pass
