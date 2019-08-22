from enum import Enum
from typing import List

from pydantic import BaseModel


class SubjectType(Enum):
    book = 1
    anime = 2
    music = 3
    game = 4
    real = 6


class SubjectImage(BaseModel):
    large: str
    common: str
    medium: str
    small: str
    grid: str


class EpisodeType(Enum):
    type0 = 0
    special = 1
    op = 2
    ed = 3
    ad = 4
    mad = 5
    other = 6


class StatusEnum(Enum):
    Air = 'Air'
    Today = 'Today'
    NA = 'NA'


class Episode(BaseModel):
    id: int
    url: str
    type: EpisodeType
    sort: int

    name: str
    name_cn: str
    duration: str
    airdate: str
    comment: int
    desc: str
    status: StatusEnum


class ApiSubject(BaseModel):
    id: int
    url: str
    type: SubjectType
    name: str
    name_cn: str
    summary: str
    air_date: str
    air_weekday: int
    images: SubjectImage
    eps: List[Episode]
