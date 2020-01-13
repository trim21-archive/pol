import datetime

import peewee as pw

from app.db_models.base import S
from app.db_models.iqiyi import IqiyiBangumi, IqiyiEpisode
from app.db_models.bilibili import BilibiliBangumi, BilibiliEpisode


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
    'Ep',
]

if __name__ == '__main__':  # pragma: no cover
    for table in [IqiyiEpisode, IqiyiBangumi, BilibiliBangumi, BilibiliEpisode]:
        table.create_table()  # type: ignore
