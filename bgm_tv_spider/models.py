import peewee as pw

import bgm_tv_spider.settings
from app.db_models import Ep as AsyncEp
from app.db_models import Relation as AsyncRelation
from app.db_models import Subject as AsyncSubject

db = pw.MySQLDatabase(
    bgm_tv_spider.settings.MYSQL_DBNAME,
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
        return cls.select().where(((cls.source == subject_id)
                                   | (cls.target == subject_id))
                                  & (cls.removed == 0))


class Ep(AsyncEp):
    class Meta(S.BaseMeta):
        database = db


class Tag(S.BgmIpViewer):
    subject_id = pw.IntegerField(primary_key=True)
    text = pw.FixedCharField(max_length=32)
    count = pw.IntegerField()


class Map(S.BgmIpViewer):
    id = pw.AutoField(primary_key=True)


class Topic(S.BgmIpViewer):
    id = pw.IntegerField()


# Subject.create_table()
# Relation.create_table()
# SubjectJson.create_table()
# Tag.create_table()
# Map.create_table()
# Ep.create_table()
# if __name__ == '__main__':
# Relation.get_relation_of_subject()
