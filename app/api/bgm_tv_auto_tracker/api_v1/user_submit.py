import peewee as pw
from fastapi import APIRouter, Depends
from peewee_async import Manager
from pydantic import BaseModel, UrlStr

from app import db_models
from app.api.bgm_tv_auto_tracker.auth import get_current_user
from app.db.depends import get_db
from app.models.bangumi_source import BangumiSourceEnum

router = APIRouter()


class ReportMissingBangumiValidator(BaseModel):
    bangumiID: str
    subjectID: str
    title: str
    href: UrlStr
    website: BangumiSourceEnum


@router.post('/missing_bangumi', include_in_schema=False)
async def report_missing_bangumi(
    data: ReportMissingBangumiValidator,
    user: db_models.UserToken = Depends(get_current_user),
    db: Manager = Depends(get_db),
):
    try:
        await db.get(
            db_models.BangumiSource,
            source=data.website,
            bangumi_id=data.bangumiID,
        )
        return {'status': 'error', 'detail': 'already has a bgm.tv subject id'}
    except pw.DoesNotExist:
        await db.execute(
            db_models.UserSubmitBangumi.replace(
                source=data.website,
                bangumi_id=data.bangumiID,
                subject_id=data.subjectID,
                user_id=user.user_id,
            )
        )
        await db.execute(
            db_models.UserToken.replace(
                source=data.website,
                bangumi_id=data.bangumiID,
                subject_id=data.subjectID,
                user_id=user.user_id,
            )
        )
        return {'status': 'success'}
