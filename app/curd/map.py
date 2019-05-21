from typing import List

import peewee as pw
from peewee_async import Manager

from app.db_models import Relation, Subject


async def get_by_subject_id(
    db: Manager, subject_id: int
) -> (List[Subject], List[Relation]):
    subject = await db.get(Subject, id=subject_id, locked=0)
    if not subject.map:
        raise pw.DoesNotExist

    nodes = await db.execute(
        Subject.select(
            Subject.id,
            Subject.map,
            Subject.name,
            Subject.info,
            Subject.image,
            Subject.name_cn,
            Subject.subject_type,
        ).where(Subject.map == subject.map)
    )
    edges = await db.execute(
        Relation.select().where(Relation.map == subject.map)
    )
    return nodes, edges
