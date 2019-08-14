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


class Relation(S.BgmIpViewer):
    id = pw.CharField(primary_key=True, index=True)
    relation = pw.CharField()
    source = pw.IntegerField()
    target = pw.IntegerField()
    map = pw.IntegerField(index=True, default=0)
    removed = pw.BooleanField(default=False)

    @classmethod
    def get_relation_of_subject(cls, subject_id):
        return cls.select().where(((cls.source == subject_id) |
                                   (cls.target == subject_id)) &
                                  (cls.removed == 0))


class Tag(S.BgmIpViewer):
    class Meta:
        primary_key = pw.CompositeKey('subject_id', 'text')

    subject_id = pw.IntegerField()
    text = pw.FixedCharField(max_length=32, index=True)
    count = pw.IntegerField()


class Map(S.BgmIpViewer):
    id = pw.AutoField(primary_key=True)


class Topic(S.BgmIpViewer):
    id = pw.IntegerField()


class UserToken(S.BgmIpViewer):
    user_id = pw.IntegerField(primary_key=True)
    scope = pw.CharField(default='')
    token_type = pw.CharField(default='')
    expires_in = pw.IntegerField(default=0)
    auth_time = pw.IntegerField(
        default=lambda: datetime.datetime.now().timestamp()
    )
    access_token = pw.FixedCharField(50, default='')
    refresh_token = pw.FixedCharField(50, default='')
    username = pw.CharField(default='')
    nickname = pw.CharField(default='')
    usergroup = pw.IntegerField(default=0)


class Ep(S.BgmIpViewer):
    subject_id = pw.IntegerField(index=True)
    ep_id = pw.IntegerField(primary_key=True)
    name = pw.CharField(max_length=400)
    episode = pw.CharField()


class EpSource(S.BgmIpViewer):
    class Meta:
        primary_key = pw.CompositeKey('source', 'source_ep_id')
        table_name = 'ep_source'

    subject_id = pw.IntegerField(index=True)
    source = pw.FixedCharField(max_length=40)
    source_ep_id = pw.CharField()
    bgm_ep_id = pw.IntegerField()
    episode = pw.IntegerField()


class BangumiSource(S.BgmIpViewer):
    class Meta:
        primary_key = pw.CompositeKey('source', 'bangumi_id')
        table_name = 'bangumi_source'

    source = pw.FixedCharField()
    bangumi_id = pw.CharField()
    """
    in bilibili, its __INITIAL_STATE__.mediaInfo.media_id
    """
    subject_id = pw.IntegerField()


class MissingBangumi(S.BgmIpViewer):
    class Meta:
        primary_key = pw.CompositeKey('source', 'bangumi_id')
        table_name = 'missing_bangumi'

    source = pw.FixedCharField()
    bangumi_id = pw.CharField()


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


class UserSubmitBangumi(S.BgmIpViewer):
    class Meta:
        table_name = 'user_submit_bangumi'
        primary_key = pw.CompositeKey('source', 'bangumi_id', 'user_id')

    source = pw.FixedCharField(max_length=40)
    subject_id = pw.IntegerField()
    bangumi_id = pw.CharField()
    user_id = pw.IntegerField()
    modify_time = pw.DateTimeField(default=datetime.datetime.now)


if __name__ == '__main__':
    from app.db.database import objects

    with objects.allow_sync():
        for table in [
            IqiyiEpisode, IqiyiBangumi, BilibiliBangumi, BilibiliEpisode
        ]:
            table.create_table()
