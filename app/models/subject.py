from enum import Enum, IntEnum

from pydantic import BaseModel


class SubjectTypeEnum(str, Enum):
    anime = 'Anime'
    book = 'Book'
    music = 'Music'
    game = 'Game'
    real = 'Real'


class LockedEnum(IntEnum):
    locked = 1
    unlocked = 0


class Subject(BaseModel):
    id: int
    name: str
    name_cn: str
    image: str = 'lain.bgm.tv/img/no_icon_subject.png'
    subject_type: SubjectTypeEnum
    locked: bool

    # tags: str
    info: dict
    score_details: dict

    score: str
    wishes: int
    done: int
    doings: int
    on_hold: int
    dropped: int

    map: int
