import peewee as pw

from app.db_models.base import S
from app.db_models.iqiyi import IqiyiBangumi, IqiyiEpisode
from app.db_models.bilibili import BilibiliBangumi, BilibiliEpisode


class Ep(S.BgmIpViewer):
    subject_id = pw.IntegerField(index=True)
    ep_id = pw.IntegerField(primary_key=True)
    name = pw.CharField(max_length=400)
    episode = pw.CharField()


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
