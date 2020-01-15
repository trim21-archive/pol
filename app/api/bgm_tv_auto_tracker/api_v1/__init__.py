from fastapi import Depends, APIRouter
from pydantic import BaseModel
from databases import Database
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.db_models import sa
from app.db.depends import get_db
from app.video_website_spider import SupportWebsite

router = APIRouter()


class SubjectIdResponse(BaseModel):
    source: str
    bangumi_id: str
    subject_id: int


@router.get(
    '/subject_id',
    response_model=SubjectIdResponse,
    responses={
        200: {'response_class': JSONResponse},
        404: {'response_class': JSONResponse, 'description': 'not found'},
    }
)
async def get_subject_id(
    bangumi_id: str,
    source: SupportWebsite,
    db: Database = Depends(get_db),
):
    if source == SupportWebsite.bilibili.value:
        r = await db.fetch_one(
            sa.select(
                [sa.BangumiBilibili]
            ).where(sa.BangumiBilibili.season_id == bangumi_id)
        )
    else:
        r = await db.fetch_one(
            sa.select(
                [sa.BangumiIqiyi]
            ).where(sa.BangumiIqiyi.bangumi_id == bangumi_id)
        )
    if not r:
        raise HTTPException(404)
    resp = {
        'source': source,
        'bangumi_id': bangumi_id,
        **r,
    }
    return resp


#
# class EpIdResponse(BaseModel):
#     subject_id: int
#     source: str
#     source_ep_id: str
#     bgm_ep_id: int
#     episode: int
#
#
# @router.get(
#     '/ep_id',
#     response_model=EpIdResponse,
#     description='get bgm.tv ep_id by website name and website episode id',
#     include_in_schema=config.DEBUG,
# )
# async def get_bgm_tv_ep_id(
#     source_ep_id: str,
#     source: SupportWebsite,
#     db: Manager = Depends(get_objects),
# ):
#     try:
#         r = await db.get(
#             db_models.EpSource,
#             source_ep_id=source_ep_id,
#             source=source,
#         )
#     except pw.DoesNotExist:
#         raise HTTPException(404)
#     return r.dict()
