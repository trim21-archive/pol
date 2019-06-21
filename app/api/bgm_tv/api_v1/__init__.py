from typing import List

from fastapi import Query, Depends, APIRouter
from pydantic import BaseModel
from peewee_async import Manager
from playhouse.shortcuts import model_to_dict

from app import models
from app.db_models import Tag, Subject
from app.db.depends import get_db

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
    limit: int = Query(20, le=50, ge=0),
    offset: int = Query(0, ge=0),
):
    q = Subject.select()
    for tag_text in tag:
        alias = Tag.alias()
        q = q.join(
            alias,
            on=((alias.subject_id == Subject.id) & (alias.text == tag_text))
        )
    count = await db.count(q.where(Subject.locked == 0))
    q = q.where(Subject.locked == 0).order_by(
        Subject.id
    ).limit(limit).offset(offset)
    return SubjectSearch(
        limit=limit,
        offset=offset,
        count=count,
        subjects=[model_to_dict(x) for x in await db.execute(q)]
    )
