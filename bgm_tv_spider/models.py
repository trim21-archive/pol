import peewee as pw

import bgm_tv_spider.settings
from app.db_models import Ep as AsyncEp
from app.db_models import Tag as AsyncTag
from app.db_models import Subject as AsyncSubject
from app.db_models import Relation as AsyncRelation

db = pw.MySQLDatabase(
    bgm_tv_spider.settings.MYSQL_DB,
    host=bgm_tv_spider.settings.MYSQL_HOST,
    charset='utf8mb4',
    user=bgm_tv_spider.settings.MYSQL_USER,
    password=bgm_tv_spider.settings.MYSQL_PASSWORD,
)


class S:
    class BaseMeta:
        database = db

    class BgmIpViewer(pw.Model):
        class Meta:
            database = db


class Subject(AsyncSubject):
    class Meta(S.BaseMeta):
        database = db


class Relation(AsyncRelation):
    class Meta(S.BaseMeta):
        database = db

    @classmethod
    def get_relation_of_subject(cls, subject_id):
        return cls.select().where(((cls.source == subject_id) |
                                   (cls.target == subject_id)) & (cls.removed == 0))


class Ep(AsyncEp):
    class Meta(S.BaseMeta):
        database = db


class Tag(AsyncTag):
    class Meta(S.BaseMeta):
        database = db
        primary_key = pw.CompositeKey('subject_id', 'text')

    subject_id = pw.IntegerField()
    text = pw.FixedCharField(max_length=32, index=True)
    count = pw.IntegerField()


class Map(S.BgmIpViewer):
    id = pw.AutoField(primary_key=True)
