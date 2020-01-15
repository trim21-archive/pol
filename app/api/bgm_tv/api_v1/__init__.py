from typing import List

from fastapi import Query, Depends, APIRouter
from pydantic import BaseModel
from databases import Database
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select, and_

from app import models
from app.db_models import sa
from app.db.depends import get_db
from app.api.bgm_tv.api_v1 import player
from app.models.subject_type import SubjectTypeEnum

router = APIRouter()
router.include_router(player.router)


class SubjectSearch(BaseModel):
    count: int
    limit: int
    offset: int
    subjects: List[models.Subject]


@router.get(
    '/subjects',
    description='and condition for many texts, '
    'ordered by subject id, maximum of limit is 50',
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
        where = (sa.Subject.locked == 0)

    query: Select = Select([sa.Subject], whereclause=where).order_by(
        sa.Subject.id
    ).limit(limit).offset(offset)

    for i, t in enumerate(tag):
        alias = aliased(sa.Tag, name=f'table_tag_{i}')

        query = query.select_from(
            sa.join(
                query.froms[0],
                alias,
                and_(alias.subject_id == sa.Subject.id, alias.text == t),
            )
        )

    return SubjectSearch(
        limit=limit,
        offset=offset,
        count=0,
        subjects=[models.Subject.parse_obj(x) async for x in db.iterate(query)],
    )


# class ListTags(BaseModel):
#     count: int
#     limit: int
#     offset: int
#     tags: List[dict]
#

# import sqlalchemy

# @router.get(
#     '/tags',
#     description='list tags and its subject counts',
#     response_model=ListTags,
#     include_in_schema=config.DEBUG,
# )
# async def list_tags(
#     db: Database = Depends(get_db),
#     limit: int = Query(20, le=50, ge=0),
#     offset: int = Query(0, ge=0),
# ):
#     query: Select = sa.select([sa.Tag.text, sa.func.count(sa.Tag)])
#     query = query.select_from(
#         join(query.froms[0], sa.Tag, sa.Subject.id == sa.Tag.subject_id)
#     ).order_by('count DESC').group_by(sa.Tag.text).limit(limit).offset(offset)
#
#     res = await db.fetch_one(query)

# res = await db.fetch_one(
#     Tag.select(
#         Tag.text,
#         pw.fn.COUNT(Subject.id).alias('count'),
#     ).join(
#         Subject,
#         'LEFT',
#         on=(Tag.subject_id == Subject.id),
#     ).group_by(Tag.text).order_by(
#         pw.SQL('count DESC')
#     ).limit(limit).offset(offset).dicts()
# )

# return ListTags(
#     limit=limit,
#     offset=offset,
#     count=await db.count(Tag.select(pw.fn.COUNT(Tag.text))),
#     tags=list(res),
# )
