from typing import Dict, Optional

import peewee as pw
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from peewee_async import Manager
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from app import db_models
from app.api.bgm_tv_auto_tracker.models import BiliBiliSubmitInfo
from app.db.depends import get_db
from app.db_models import BangumiSource
from app.models.bangumi_source import BangumiSourceEnum

from . import user_submit

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')

router = APIRouter()
router.include_router(user_submit.router)


class SubjectIDQuery(BaseModel):
    website: BangumiSourceEnum
    bangumi_id: str


class SubjectIdResponse(BaseModel):
    source: str
    bangumi_id: str
    subject_id: int
    eps_map: Optional[Dict[str, int]]


@router.get(
    '/subject_id/{source}/{bangumi_id}',
    response_model=SubjectIdResponse,
    include_in_schema=False
)
async def get_subject_id(
    bangumi_id: str,
    source: BangumiSourceEnum,
    db: Manager = Depends(get_db),
):
    try:
        r = await db.get(
            BangumiSource,
            bangumi_id=bangumi_id,
            source=source,
        )
    except pw.DoesNotExist:
        raise HTTPException(404)
    eps_map = await db.execute(
        db_models.EpSource.select().where(
            db_models.EpSource.source == source,
            db_models.EpSource.subject_id == r.subject_id,
        )
    )
    resp = r.dict()
    resp['eps_map'] = [db_models.model_to_dict(x) for x in eps_map]
    return resp


@router.get('/eps/{source}/{bangumi_id}', include_in_schema=False)
async def get_eps(
    source_ep_id: str,
    source: BangumiSourceEnum,
    db: Manager = Depends(get_db),
):
    try:
        r = await db.get(
            db_models.EpSource,
            source_ep_id=source_ep_id,
            source=source,
        )
    except pw.DoesNotExist:
        raise HTTPException(404)
    return r.dict()


class EpIdResponse(BaseModel):
    subject_id: int
    source: str
    source_ep_id: str
    bgm_ep_id: int
    episode: int


@router.get(
    '/ep_id/{source}/{source_ep_id}',
    response_model=EpIdResponse,
    include_in_schema=False
)
async def get_bgm_tv_ep_id(
    source_ep_id: str,
    source: BangumiSourceEnum,
    db: Manager = Depends(get_db),
):
    try:
        r = await db.get(
            db_models.EpSource,
            source_ep_id=source_ep_id,
            source=source,
        )
    except pw.DoesNotExist:
        raise HTTPException(404)
    return r.dict()


@router.post('/collect_episode_info', include_in_schema=False)
async def collect_episode_info(info: BiliBiliSubmitInfo):
    return info.dict()
