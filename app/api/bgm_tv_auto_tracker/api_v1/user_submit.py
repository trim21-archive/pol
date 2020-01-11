import peewee as pw
from fastapi import Depends, APIRouter
from pydantic import BaseModel
from peewee_async import Manager
from starlette.responses import JSONResponse

from app import db_models
from app.core import config
from app.db.depends import get_db
from app.video_website_spider import SupportWebsite
from app.api.auth.api_v1.depends import get_current_user

router = APIRouter()


class ReportSubjectID(BaseModel):
    source: SupportWebsite
    bangumi_id: str
    subject_id: int


@router.post(
    '/submit/subject_id',
    include_in_schema=config.DEBUG,
    # responses={
    # '200': JSONResponse,
    # 400: {'content': JSONResponse},
    # }
)
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
        return JSONResponse({'status': 'error', 'detail': 'object already exists'}, 400)
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
