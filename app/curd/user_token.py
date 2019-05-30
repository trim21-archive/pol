import datetime

from peewee_async import Manager

from app.db_models import UserToken


async def upsert(
    db: Manager,
    user_id: int,
    access_token: str = None,
    refresh_token: str = None,
    expires_in: str = None,
    token_type: str = None,
    scope: str = None,
    auth_time: int = None,
) -> UserToken:
    return await db.execute(
        UserToken.replace(
            user_id=user_id,
            scope=scope or '',
            token_type=token_type,
            expires_in=expires_in,
            access_token=access_token,
            refresh_token=refresh_token,
            auth_time=auth_time or datetime.datetime.now().timestamp(),
        )
    )


async def get_by_user_id(db: Manager, user_id: int):
    return await db.get(UserToken, user_id)
