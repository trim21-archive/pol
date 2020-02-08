from typing import List

from pydantic import Json, BaseModel

from app.models.subject_type import SubjectTypeEnum


class Edges(BaseModel):
    id: str
    relation: str
    source: int
    target: int
    map: int


class Nodes(BaseModel):
    id: int
    subject_id: int
    name: str
    name_cn: str
    image: str = 'lain.bgm.tv/img/no_icon_subject.png'
    subject_type: SubjectTypeEnum
    info: Json
    map: int


class Map(BaseModel):
    edges: List[Edges]
    nodes: List[Nodes]
