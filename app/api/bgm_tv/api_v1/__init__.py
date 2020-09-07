from typing import List

from fastapi import Query, Depends, APIRouter
from pydantic import BaseModel
from databases import Database
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select, and_

from app import models
from app.db_models import sa
from app.db.depends import get_db
from app.models.subject_type import SubjectTypeEnum

router = APIRouter()


class SubjectSearch(BaseModel):
    count: int
    limit: int
    offset: int
    subjects: List[models.Subject]


@router.get(
    "/subjects",
    description="and condition for many texts, "
    "ordered by subject id, maximum of limit is 50",
    response_model=SubjectSearch,
)
async def search_by_tag(
    tag: List[str] = Query(..., min_length=1),
    db: Database = Depends(get_db),
    subject_type: SubjectTypeEnum = None,
    limit: int = Query(20, le=50, ge=0),
    offset: int = Query(0, ge=0),
):
    if subject_type is not None:
        where = and_(
            sa.Subject.locked == 0, sa.Subject.subject_type == subject_type.value
        )

    else:
        where = sa.Subject.locked == 0

    query: Select = (
        Select([sa.Subject], whereclause=where)
        .order_by(sa.Subject.id)
        .limit(limit)
        .offset(offset)
    )

    for i, t in enumerate(tag):
        alias = aliased(sa.Tag, name=f"table_tag_{i}")

        query = query.select_from(
            sa.join(
                query.froms[0],
                alias,
                and_(alias.subject_id == sa.Subject.id, alias.text == t),
            )
        )
    return {
        "limit": limit,
        "offset": offset,
        "count": 0,
        "subjects": await db.fetch_all(query),
    }
