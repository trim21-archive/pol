from sqlalchemy import CHAR, Column, Integer

from app.db.base import Base


class Tag(Base):
    subject_id = Column(Integer, primary_key=True)
    text = Column(CHAR, max_length=32)
    count = Column(Integer)
