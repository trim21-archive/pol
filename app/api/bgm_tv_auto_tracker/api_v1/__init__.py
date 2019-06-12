import peewee as pw
from fastapi import Depends, APIRouter
from pydantic import BaseModel
from peewee_async import Manager
from starlette.exceptions import HTTPException

from app import db_models
from app.db_models import BangumiSource
from app.db.depends import get_db
from app.models.bangumi_source import BangumiSourceEnum
from app.api.bgm_tv_auto_tracker.models import BiliBiliSubmitInfo

from . import user_submit

router = APIRouter()
router.include_router(user_submit.router)


class SubjectIdResponse(BaseModel):
    source: str
    bangumi_id: str
    subject_id: int


@router.get('/subject_id', response_model=SubjectIdResponse)
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
    resp = r.dict()
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
