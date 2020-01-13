from typing import Tuple

from databases import Database

from app.curd import subject
from app.db_models import sa


async def get_by_subject_id(
    db: Database,
    subject_id: int,
) -> Tuple[list, list]:
    s = await subject.get(
        db,
        sa.Subject.id == subject_id,
        sa.Subject.locked == 0,
        sa.Subject.map != 0,
    )

    nodes = await db.fetch_all(
        sa.select([
            sa.Subject.id,
            sa.Subject.map,
            sa.Subject.name,
            sa.Subject.info,
            sa.Subject.image,
            sa.Subject.name_cn,
            sa.Subject.subject_type,
        ]).where(sa.Subject.map == s.map).where(s.locked != 0)
    )

    edges = await db.fetch_all(sa.select([sa.Relation]).where(sa.Relation.map == s.map))
    return nodes, edges
