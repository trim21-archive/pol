from fastapi import Depends
from peewee_async import Manager

from app.api.bgm_tv_auto_tracker.auth.session import SessionValue, get_session
from app.db.depends import get_db
from app.db_models import UserToken


async def get_current_user(
    session: SessionValue = Depends(get_session),
    db: Manager = Depends(get_db),
):
    return await db.get(UserToken, user_id=session.user_id)
