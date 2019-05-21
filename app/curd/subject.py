from peewee_async import Manager

from app.db_models import Subject


async def get_by_id(db: Manager, subject_id) -> Subject:
    return await db.get(Subject, id=subject_id)
