from sqlalchemy import Column, Integer, String

from app.db.base import Base


class Subject(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, )
    image = Column(String, )
    subject_type = Column(String, )
    name_cn = Column(String, )
    locked = Column(Integer, default=0)

    tags = Column(String, )
    info = Column(String, )
    score_details = Column(String, )

    score = Column(String, )
    wishes = Column(Integer, default=0)
    done = Column(Integer, default=0)
    doings = Column(Integer, default=0)
    on_hold = Column(Integer, default=0)
    dropped = Column(Integer, default=0)

    map = Column(Integer, default=0, index=True)

    def __repr__(self):
        return f'<Subject {self.id} {self.name} >'
