from enum import IntEnum

from pydantic import BaseModel

from app.models.subject_type import SubjectTypeEnum


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
