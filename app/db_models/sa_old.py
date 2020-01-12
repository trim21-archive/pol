from sqlalchemy import CHAR, Text, Column, String, DateTime, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT, LONGTEXT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class BangumiBilibili(Base):
    __tablename__ = 'bangumi_bilibili'

    subject_id = Column(INTEGER(11), primary_key=True)
    media_id = Column(INTEGER(11), nullable=False, index=True)
    season_id = Column(INTEGER(11), nullable=False)
    title = Column(String(255), nullable=False)


class BangumiIqiyi(Base):
    __tablename__ = 'bangumi_iqiyi'

    subject_id = Column(INTEGER(11), primary_key=True)
    bangumi_id = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False)


class BangumiSource(Base):
    __tablename__ = 'bangumi_source'

    source = Column(CHAR(255), primary_key=True, nullable=False)
    bangumi_id = Column(String(255), primary_key=True, nullable=False)
    subject_id = Column(INTEGER(11), nullable=False)


class BgmTimeline(Base):
    __tablename__ = 'bgm_timeline'

    id = Column(BIGINT(20), primary_key=True)
    user_name = Column(String(255), nullable=False, index=True)
    user_id = Column(INTEGER(11), nullable=False, index=True)
    time = Column(INTEGER(11), nullable=False, index=True)


class Ep(Base):
    __tablename__ = 'ep'

    ep_id = Column(INTEGER(11), primary_key=True)
    subject_id = Column(INTEGER(11), nullable=False, index=True)
    name = Column(String(400), nullable=False)
    episode = Column(String(255), nullable=False)


class EpBilibili(Base):
    __tablename__ = 'ep_bilibili'

    source_ep_id = Column(INTEGER(11), primary_key=True)
    ep_id = Column(INTEGER(11), nullable=False)
    subject_id = Column(INTEGER(11), nullable=False)
    title = Column(String(255), nullable=False)


class EpIqiyi(Base):
    __tablename__ = 'ep_iqiyi'

    source_ep_id = Column(String(255), primary_key=True)
    ep_id = Column(INTEGER(11), nullable=False)
    subject_id = Column(INTEGER(11), nullable=False)
    title = Column(String(255), nullable=False)


class EpSource(Base):
    __tablename__ = 'ep_source'

    subject_id = Column(INTEGER(11), nullable=False, index=True)
    source = Column(CHAR(40), primary_key=True, nullable=False)
    source_ep_id = Column(String(255), primary_key=True, nullable=False)
    bgm_ep_id = Column(INTEGER(11), nullable=False)
    episode = Column(INTEGER(11), nullable=False)


class Map(Base):
    __tablename__ = 'map'

    id = Column(INTEGER(11), primary_key=True)


class MissingBangumi(Base):
    __tablename__ = 'missing_bangumi'

    source = Column(CHAR(255), primary_key=True, nullable=False)
    bangumi_id = Column(String(255), primary_key=True, nullable=False)


class Relation(Base):
    __tablename__ = 'relation'

    id = Column(String(255), primary_key=True)
    relation = Column(String(255), nullable=False)
    source = Column(INTEGER(11), nullable=False)
    target = Column(INTEGER(11), nullable=False)
    map = Column(INTEGER(11), nullable=False, index=True, server_default=text("'0'"))
    removed = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


class Subject(Base):
    __tablename__ = 'subject'

    id = Column(INTEGER(11), primary_key=True)
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


class Subjectjson(Base):
    __tablename__ = 'subjectjson'

    id = Column(INTEGER(11), primary_key=True)
    info = Column(LONGTEXT, nullable=False)


class Tag(Base):
    __tablename__ = 'tag'

    subject_id = Column(INTEGER(11), primary_key=True, nullable=False)
    text = Column(CHAR(32), primary_key=True, nullable=False, index=True)
    count = Column(INTEGER(11), nullable=False)


class UserSubmitBangumi(Base):
    __tablename__ = 'user_submit_bangumi'

    source = Column(CHAR(40), primary_key=True, nullable=False)
    subject_id = Column(INTEGER(11), nullable=False)
    bangumi_id = Column(String(255), primary_key=True, nullable=False)
    user_id = Column(INTEGER(11), primary_key=True, nullable=False)
    modify_time = Column(DateTime, nullable=False)


class Usertoken(Base):
    __tablename__ = 'usertoken'

    user_id = Column(INTEGER(11), primary_key=True)
    scope = Column(String(255), nullable=False)
    token_type = Column(String(255), nullable=False)
    expires_in = Column(INTEGER(11), nullable=False)
    auth_time = Column(INTEGER(11), nullable=False)
    access_token = Column(CHAR(50), nullable=False)
    refresh_token = Column(CHAR(50), nullable=False)
    username = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=False)
    usergroup = Column(INTEGER(11), nullable=False)
