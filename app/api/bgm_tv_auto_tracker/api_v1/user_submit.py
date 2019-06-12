import peewee as pw
from fastapi import Depends, APIRouter
from pydantic import UrlStr, BaseModel
from peewee_async import Manager

from app import db_models
from app.core import config
from app.db.depends import get_db
from app.models.bangumi_source import BangumiSourceEnum
from app.api.bgm_tv_auto_tracker.auth import get_current_user

router = APIRouter()


class ReportMissingBangumiValidator(BaseModel):
    bangumiID: str
    subjectID: str
    title: str
    href: UrlStr
    website: BangumiSourceEnum


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
    result: db_models.UserSubmitBangumi = await db.execute(
        db_models.UserSubmitBangumi.replace(
            source=data.source,
            subject_id=data.subject_id,
            bangumi_id=data.bangumi_id,
            user_id=current_user.user_id,
        )
    )
    return result


@router.post('/submit/missing_bangumi', include_in_schema=config.DEBUG)
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
