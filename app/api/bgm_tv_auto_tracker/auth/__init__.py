import peewee as pw
from fastapi import Depends
from peewee_async import Manager
from starlette.exceptions import HTTPException

from app.db_models import UserToken
from app.db.depends import get_db
from app.api.bgm_tv_auto_tracker.auth.session import SessionValue, get_session


async def get_current_user(
    session: SessionValue = Depends(get_session),
    db: Manager = Depends(get_db),
):
    try:
        return await db.get(UserToken, user_id=session.user_id)
    except pw.DoesNotExist:
        raise HTTPException(403)
