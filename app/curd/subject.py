from typing import List

from databases import Database

from app.db_models import sa
from app.curd.exceptions import NotFoundError


async def select(db: Database, *where) -> List[sa.Subject]:
    query = sa.select([sa.Subject])
    for w in where:
        query = query.where(w)
    return [sa.Subject(**r) for r in await db.fetch_all(query)]


async def get(db: Database, *where) -> sa.Subject:
    query = sa.select([sa.Subject])
    for w in where:
        query = query.where(w)
    r = await db.fetch_one(query)
    try:
        return sa.Subject(**r)
    except Exception:
        raise NotFoundError()


async def get_by_id(db: Database, subject_id) -> sa.Subject:
    return await get(db, sa.Subject.id == subject_id)
