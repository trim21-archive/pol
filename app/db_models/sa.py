from typing import TypeVar

import sqlalchemy.ext.declarative.api
from sqlalchemy import (
    CHAR,
    Text,
    Column,
    String,
    DateTime,
    func,
    join,
    text,
    select,
    update,
)
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, insert
from sqlalchemy.ext.declarative import declarative_base

T = TypeVar("T", bound=sqlalchemy.ext.declarative.api.DeclarativeMeta)


class ORMMixin:
    def dict(self: T):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d


Base: sqlalchemy.ext.declarative.api.DeclarativeMeta = declarative_base()
metadata = Base.metadata


class BangumiBilibili(Base, ORMMixin):
    name = "bilibili"
    __tablename__ = "bangumi_bilibili"

    subject_id = Column(INTEGER(11), primary_key=True, autoincrement=False)
    media_id = Column(INTEGER(11), nullable=False, index=True)
    season_id = Column(INTEGER(11), nullable=False, index=True)
    title = Column(String(255), nullable=False)

    @property
    def url(self):
        return f"https://www.bilibili.com/bangumi/media/md{self.media_id}/"

    @property
    def bangumi_id(self):
        return self.season_id


class BangumiIqiyi(Base, ORMMixin):
    name = "iqiyi"
    __tablename__ = "bangumi_iqiyi"

    subject_id = Column(INTEGER(11), primary_key=True, autoincrement=False)
    bangumi_id = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False)

    @property
    def url(self):
        return f"https://www.iqiyi.com/{self.bangumi_id}.html"


class BangumiSource(Base, ORMMixin):
    __tablename__ = "bangumi_source"

    source = Column(CHAR(255), primary_key=True, nullable=False)
    bangumi_id = Column(String(255), primary_key=True, nullable=False)
    subject_id = Column(INTEGER(11), nullable=False)


class Ep(Base, ORMMixin):
    __tablename__ = "ep"

    ep_id = Column(INTEGER(11), primary_key=True, autoincrement=False)
    subject_id = Column(INTEGER(11), nullable=False, index=True)
    name = Column(String(400), nullable=False)
    episode = Column(String(255), nullable=False)


class EpBilibili(Base, ORMMixin):
    __tablename__ = "ep_bilibili"

    source_ep_id = Column(INTEGER(11), primary_key=True, autoincrement=False)
    ep_id = Column(INTEGER(11), nullable=False)
    subject_id = Column(INTEGER(11), nullable=False)
    title = Column(String(255), nullable=False)


class EpIqiyi(Base, ORMMixin):
    __tablename__ = "ep_iqiyi"

    source_ep_id = Column(String(255), primary_key=True, autoincrement=False)
    ep_id = Column(INTEGER(11), nullable=False)
    subject_id = Column(INTEGER(11), nullable=False)
    title = Column(String(255), nullable=False)


class EpSource(Base, ORMMixin):
    __tablename__ = "ep_source"

    subject_id = Column(INTEGER(11), nullable=False, index=True, autoincrement=False)
    source = Column(CHAR(40), primary_key=True, nullable=False)
    source_ep_id = Column(String(255), primary_key=True, nullable=False)
    bgm_ep_id = Column(INTEGER(11), nullable=False)
    episode = Column(INTEGER(11), nullable=False)


class MissingBangumi(Base, ORMMixin):
    __tablename__ = "missing_bangumi"

    source = Column(CHAR(255), primary_key=True, nullable=False)
    bangumi_id = Column(String(255), primary_key=True, nullable=False)


class Relation(Base, ORMMixin):
    __tablename__ = "relation"

    id = Column(String(255), primary_key=True)
    relation = Column(String(255), nullable=False)
    source = Column(INTEGER(11), nullable=False)
    target = Column(INTEGER(11), nullable=False)
    map = Column(INTEGER(11), nullable=False, index=True, server_default=text("'0'"))
    removed = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class Subject(Base, ORMMixin):
    __tablename__ = "subject"

    id = Column(INTEGER(11), primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=False)
    image = Column(String(255), nullable=False)
    subject_type = Column(String(255), nullable=False)
    name_cn = Column(String(255), nullable=False)
    tags = Column(Text, nullable=False)
    info = Column(Text, nullable=False)
    score_details = Column(Text, nullable=False)
    score = Column(String(255), nullable=False)
    wishes = Column(INTEGER(255), nullable=False, server_default=text("'0'"))
    done = Column(INTEGER(255), nullable=False, server_default=text("'0'"))
    doings = Column(INTEGER(255), nullable=False, server_default=text("'0'"))
    on_hold = Column(INTEGER(255), nullable=False, server_default=text("'0'"))
    dropped = Column(INTEGER(255), nullable=False, server_default=text("'0'"))
    map = Column(INTEGER(11), nullable=False, index=True, server_default=text("'0'"))
    locked = Column(TINYINT(1), nullable=False)

    def __str__(self):
        return f"<Subject id={self.id} name={self.name_cn} name_cn={self.name_cn}>"

    __repr__ = __str__


class Tag(Base, ORMMixin):
    __tablename__ = "tag"

    subject_id = Column(INTEGER(11), primary_key=True, nullable=False)
    text = Column(CHAR(32), primary_key=True, nullable=False, index=True)
    count = Column(INTEGER(11), nullable=False)


class UserSubmitBangumi(Base, ORMMixin):
    __tablename__ = "user_submit_bangumi"

    source = Column(CHAR(40), primary_key=True, nullable=False)
    subject_id = Column(INTEGER(11), nullable=False)
    bangumi_id = Column(String(255), primary_key=True, nullable=False)
    user_id = Column(INTEGER(11), primary_key=True, nullable=False)
    modify_time = Column(DateTime, nullable=False)


class UserToken(Base, ORMMixin):
    __tablename__ = "usertoken"

    user_id = Column(INTEGER(11), primary_key=True, autoincrement=False)
    scope = Column(String(255), nullable=False)
    token_type = Column(String(255), nullable=False)
    expires_in = Column(INTEGER(11), nullable=False)
    auth_time = Column(INTEGER(11), nullable=False)
    access_token = Column(CHAR(50), nullable=False)
    refresh_token = Column(CHAR(50), nullable=False)
    username = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=False)
    usergroup = Column(INTEGER(11), nullable=False)


__all__ = [
    "func",
    "update",
    "insert",
    "select",
    "join",
    "metadata",
    "BangumiBilibili",
    "BangumiIqiyi",
    "BangumiSource",
    "Ep",
    "EpBilibili",
    "EpIqiyi",
    "EpSource",
    "MissingBangumi",
    "Relation",
    "Subject",
    "Tag",
    "UserSubmitBangumi",
    "UserToken",
]
if __name__ == "__main__":
    from databases import DatabaseURL
    from sqlalchemy import create_engine

    from app.core import config

    engine = create_engine(
        str(DatabaseURL(config.MYSQL_URI).replace(dialect="mysql+pymysql"))
    )
    Base.metadata.create_all(engine)
