from sqlalchemy import Column, Integer

from app.db.base import Base


class Topic(Base):
    id = Column(Integer, primary_key=True)
