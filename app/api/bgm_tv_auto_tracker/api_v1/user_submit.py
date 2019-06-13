import peewee as pw
from fastapi import Depends, APIRouter
from pydantic import BaseModel
from peewee_async import Manager
from starlette.responses import JSONResponse

from app import db_models
from app.core import config
from app.db.depends import get_db
from app.models.bangumi_source import BangumiSourceEnum
from app.api.bgm_tv_auto_tracker.auth import get_current_user

router = APIRouter()


class ReportSubjectID(BaseModel):
    bangumi_id: str
    source: BangumiSourceEnum
    subject_id: int


@router.post('/submit/subject_id', include_in_schema=config.DEBUG)
async def submit_subject_id(
    data: ReportSubjectID,
    current_user: db_models.UserToken = Depends(get_current_user),
    db: Manager = Depends(get_db),
):
    try:
        await db.get(
            db_models.BangumiSource,
            source=data.source,
            bangumi_id=data.bangumi_id,
            subject_id=data.subject_id,
        )
        return JSONResponse({
            'status': 'error', 'detail': 'object already exists'
        }, 400)
    except pw.DoesNotExist:
        result: db_models.UserSubmitBangumi = await db.execute(
            db_models.UserSubmitBangumi.replace(
                source=data.source,
                subject_id=data.subject_id,
                bangumi_id=data.bangumi_id,
                user_id=current_user.user_id,
            )
        )
        return result
