from enum import Enum
from typing import List, Union

from fastapi import Depends
from pydantic import HttpUrl, BaseModel
from databases import Database

from app.log import logger
from app.api.auth import api_v1 as auth
from app.db_models import sa
from app.video_website_spider import SupportWebsite


class SubmitResult(BaseModel):
    website: SupportWebsite
    url: str


class PlayerEpisode(BaseModel):
    url: str
    subject_id: int
    source_ep_id: str
    website: SupportWebsite


class SubmitBody(BaseModel):
    url: HttpUrl


# @router.get(
#     '/ep/player/{ep_id}',
#     description='**unstable**\n\n提交条目对应的视频网站合集地址.',
#     response_model=List[PlayerEpisode],
# )
# async def get_player_url_of_episode(
#     ep_id: int,
#     db: Database = Depends(get_db),
# ):
#     return [{
#         'website': x.name,
#         'url': x.url,
#         'subject_id': x.subject_id,
#         'source_ep_id': x.source_ep_id,
#     } for x in await get_all_episode_player(db, ep_id)]

#
# @router.put(
#     '/subject/player/{subject_id}',
#     description='**unstable**\n\n针对bgm.tv的单集获取视频网站播放地址.',
#     response_model=SubmitResult,
# )
# async def submit_player_url_for_subject(
#     subject_id: int,
#     submit: SubmitBody,
#     current_user: sa.UserToken = Depends(auth.get_current_user),
# ):
#     website = worker.dispatcher.get_website(submit.url)
#     if not website:
#         raise HTTPException(422, "url not correct, don't match any valid pattern")
#     handler = worker.dispatcher.get_handler(website)
#     try:
#         handler.valid_subject_url(submit.url)
#         worker.submit_bangumi.delay(subject_id, submit.url)
#         logger.bind(
#             event='submit.bangumi',
#             kwargs={
#                 'user': current_user.user_id,
#                 'url': submit.url,
#             },
#         ).info(
#             'user<{}> submit bangumi player page {}',
#             current_user.user_id,
#             submit.url,
#         )
#
#         return {'website': website, 'url': submit.url}
#     except UrlNotValidError as e:
#         raise HTTPException(422, 'url not correct, should match ' + e.pattern)

# @router.put(
#     '/ep/player/{ep_id}',
#     description='针对bgm.tv的单集获取视频网站播放地址.\n\n',
#     response_model=SubmitResult,
# )
# async def submit_player_url_for_episode(
#     ep_id: int,
#     submit: SubmitBody,
#     current_user: sa.UserToken = Depends(auth.get_current_user),
# ):
#     website = worker.dispatcher.get_website(submit.url)
#     if not website:
#         raise HTTPException(422, "url not correct, don't match any valid pattern")
#     handler = worker.dispatcher.get_handler(website)
#     try:
#         handler.valid_ep_url(submit.url)
#         worker.submit_ep.delay(ep_id, submit.url)
#         logger.bind(
#             event='submit.ep',
#             kwargs={
#                 'user': current_user.user_id,
#                 'url': submit.url,
#             }
#         ).info(
#             'user<{}> submit episode player page {}',
#             current_user.user_id,
#             submit.url,
#         )
#         return {'website': website, 'url': submit.url}
#     except UrlNotValidError as e:
#         raise HTTPException(422, 'url not correct, should match ' + e.pattern)


class ErrorTypeEnum(str, Enum):
    subject = "subject"
    sort = "sort"


class PostError(BaseModel):
    url: HttpUrl
    error: ErrorTypeEnum


class PostSubjectInfo(PostError):
    subject_id: int


class PostEpInfo(PostError):
    ep_id: int


# @router.post(
#     '/subject/player/{subject_id}',
# )
# async def set_subject_player_url_status(
#     subject_id: int,
#     data: PostSubjectInfo,
#     current_user: sa.UserToken = Depends(auth.get_current_user),
#     db: Database = Depends(get_db),
# ):
#     logger.bind(
#         event='user.submit.subject.error',
#         kwargs={
#             'user_id': current_user.user_id,
#             'subject_id': subject_id,
#             'url': data.url,
#         },
#     ).info('user {} submit error {}', current_user.user_id, subject_id)


# @router.post(
#     '/subject/ep/{ep_id}',
# )
async def set_ep_player_url_status(
    ep_id: int,
    data: PostEpInfo,
    current_user: sa.UserToken = Depends(auth.get_current_user),
):
    logger.bind(
        event="user.submit.ep.error",
        kwargs={"user_id": current_user.user_id, "subject_id": ep_id, "url": data.url,},
    ).info("")


async def get_all_episode_player(
    db: Database, ep_id: int,
) -> List[Union[sa.EpBilibili, sa.EpIqiyi]]:
    episodes = []
    for model in (sa.EpBilibili, sa.EpIqiyi):
        r = await db.fetch_one(sa.select([model]).where(model.ep_id == ep_id))
        if r:
            episodes.append(model(**r))
    return episodes
