from typing import List

import peewee as pw
from fastapi import Query, Depends, APIRouter
from pydantic import BaseModel
from peewee_async import Manager
from playhouse.shortcuts import model_to_dict

from app import models
from app.core import config
from app.db_models import Tag, Subject
from app.db.depends import get_db
from app.models.subject_type import SubjectTypeEnum

router = APIRouter()


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
    db: Manager = Depends(get_db),
    subject_type: SubjectTypeEnum = None,
    limit: int = Query(20, le=50, ge=0),
    offset: int = Query(0, ge=0),
):
    q = Subject.select()

    for tag_text in tag:
        alias = Tag.alias()
        q = q.join(
            alias, on=((alias.subject_id == Subject.id) & (alias.text == tag_text))
        )

    where = Subject.locked == 0
    if subject_type is not None:
        where = where & (Subject.subject_type == subject_type)
    q = q.where(where)

    count = await db.count(q)
    q = q.order_by(Subject.id).limit(limit).offset(offset)
    return SubjectSearch(
        limit=limit,
        offset=offset,
        count=count,
        subjects=[model_to_dict(x) for x in await db.execute(q)]
    )


class ListTags(BaseModel):
    count: int
    limit: int
    offset: int
    tags: List[dict]


@router.get(
    '/tags',
    description='list tags and its subject counts',
    response_model=ListTags,
    include_in_schema=config.DEBUG,
)
async def list_tags(
    db: Manager = Depends(get_db),
    limit: int = Query(20, le=50, ge=0),
    offset: int = Query(0, ge=0),
):
    res = await db.execute(
        Tag.select(
            Tag.text,
            pw.fn.COUNT(Subject.id).alias('count'),
        ).join(
            Subject,
            'LEFT',
            on=(Tag.subject_id == Subject.id),
        ).group_by(Tag.text).order_by(
            pw.SQL('count DESC')
        ).limit(limit).offset(offset).dicts()
    )

    return ListTags(
        limit=limit,
        offset=offset,
        count=await db.count(Tag.select(pw.fn.COUNT(Tag.text))),
        tags=[x for x in res],
    )
