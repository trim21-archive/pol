import json
import datetime

import peewee as pw

from app.db_models.base import S
from app.db_models.iqiyi import IqiyiBangumi, IqiyiEpisode
from app.db_models.bilibili import BilibiliBangumi, BilibiliEpisode


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


class Tag(S.BgmIpViewer):
    class Meta:
        primary_key = pw.CompositeKey('subject_id', 'text')

    subject_id = pw.IntegerField()
    text = pw.FixedCharField(max_length=32, index=True)
    count = pw.IntegerField()


class Ep(S.BgmIpViewer):
    subject_id = pw.IntegerField(index=True)
    ep_id = pw.IntegerField(primary_key=True)
    name = pw.CharField(max_length=400)
    episode = pw.CharField()


class UserSubmitEpisode(S.BgmIpViewer):
    class Meta:
        table_name = 'user_submit_episode'

    source = pw.FixedCharField(max_length=40)
    source_ep_id = pw.CharField()
    bgm_ep_id = pw.IntegerField()
    episode = pw.IntegerField()
    user_id = pw.IntegerField()
    create_time = pw.DateTimeField(default=datetime.datetime.now)
    modify_time = pw.DateTimeField(default=datetime.datetime.now)


__all__ = [
    'IqiyiBangumi',
    'IqiyiEpisode',
    'BilibiliBangumi',
    'BilibiliEpisode',
    'Subject',
    'Tag',
    'Ep',
]

if __name__ == '__main__':  # pragma: no cover
    for table in [IqiyiEpisode, IqiyiBangumi, BilibiliBangumi, BilibiliEpisode]:
        table.create_table()  # type: ignore
