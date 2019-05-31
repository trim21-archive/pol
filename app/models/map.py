from enum import Enum
from typing import List

from pydantic import BaseModel


class SubjectTypeEnum(str, Enum):
    anime = 'Anime'
    book = 'Book'
    music = 'Music'
    game = 'Game'
    real = 'Real'


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
    image: str = 'lain.bgm_tv_spider.tv/img/no_icon_subject.png'
    subject_type: SubjectTypeEnum
    info: dict
    map: int


class Map(BaseModel):
    edges: List[Edges]
    nodes: List[Nodes]
