import json

import peewee as pw
from playhouse.shortcuts import model_to_dict

from app.db.database import db


class MyJSONField(pw.TextField):
    def python_value(self, value):
        if value is not None:
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return value

    def db_value(self, value):
        if value is not None:
            return json.dumps(value)


class S:
    class BgmIpViewer(pw.Model):
        class Meta:
            database = db

        def dict(self):
            return model_to_dict(self)

        def __iter__(self):
            yield from self.dict()


class Subject(S.BgmIpViewer):
    id = pw.IntegerField(primary_key=True, index=True)
    name = pw.CharField()
    image = pw.CharField()
    subject_type = pw.CharField()
    name_cn = pw.CharField()
    locked = pw.BooleanField(default=False)

    tags = pw.TextField()
    info = MyJSONField()
    score_details = MyJSONField()

    score = pw.CharField()
    wishes = pw.IntegerField(default=0)
    done = pw.IntegerField(default=0)
    doings = pw.IntegerField(default=0)
    on_hold = pw.IntegerField(default=0)
    dropped = pw.IntegerField(default=0)

    map = pw.IntegerField(index=True, default=0)

    def __repr__(self):
        return f'<Subject id={self.id}, name={self.name}>'

    __str__ = __repr__


class Relation(S.BgmIpViewer):
    id = pw.CharField(primary_key=True, index=True)
    relation = pw.CharField()
    source = pw.IntegerField()
    target = pw.IntegerField()
    map = pw.IntegerField(index=True, default=0)
    removed = pw.BooleanField(default=False)

    @classmethod
    def get_relation_of_subject(cls, subject_id):
        return cls.select().where(((cls.source == subject_id)
                                   | (cls.target == subject_id))
                                  & (cls.removed == 0))


class Tag(S.BgmIpViewer):
    subject_id = pw.IntegerField(primary_key=True)
    text = pw.FixedCharField(max_length=32)
    count = pw.IntegerField()


class LongTextField(pw._StringField):
    field_type = 'LONGTEXT'


class SubjectJson(S.BgmIpViewer):
    id = pw.IntegerField(primary_key=True, index=True)
    info = LongTextField()


class Map(S.BgmIpViewer):
    id = pw.AutoField(primary_key=True)


class Topic(S.BgmIpViewer):
    id = pw.IntegerField()


class Info(S.BgmIpViewer):
    subject_id = pw.IntegerField(primary_key=True)
    key = pw.CharField()
    value = pw.CharField()
