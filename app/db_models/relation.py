from sqlalchemy import Column, Integer, String, and_, or_
from sqlalchemy.orm import Session

from app.db.base import Base


class Relation(Base):
    id = Column(String, primary_key=True, index=True)
    relation = Column(String)
    source = Column(Integer)
    target = Column(Integer)
    map = Column(Integer, index=True, default=0)
    removed = Column(Integer, default=0)

    @classmethod
    def get_relation_of_subject(cls, session: Session, subject_id):
        return session.query(cls).filter(
            and_(
                cls.removed == 0,
                or_(cls.source == subject_id, cls.target == subject_id)
            ),
        )
