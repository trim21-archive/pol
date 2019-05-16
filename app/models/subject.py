from pydantic import BaseModel


class Subject(BaseModel):
    id: int
    name: str
    image: str
    subject_type: str
    name_cn: str
    locked: int

    tags: str
    info: str
    score_details: str

    score: str
    wishes: int
    done: int
    doings: int
    on_hold: int
    dropped: int

    map: int
