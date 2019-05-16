from sqlalchemy import Column, Integer

from app.db import Base


class Map(Base):
    id = Column(Integer, primary_key=True)
