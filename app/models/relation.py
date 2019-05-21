from pydantic import BaseModel


class Relation(BaseModel):
    id: str
    relation: str
    source: int
    target: int
    map: int
    removed: bool
