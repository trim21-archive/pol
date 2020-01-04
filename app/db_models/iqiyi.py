import peewee as pw

from app.db_models.base import S


class IqiyiBangumi(S.BgmIpViewer):
    """
    db table for iqiyi bangumi
    """
    name = 'iqiyi'

    class Meta:
        table_name = 'bangumi_iqiyi'

    subject_id = pw.IntegerField(primary_key=True)

    bangumi_id = pw.CharField(index=True)
    title = pw.CharField(default='')

    @property
    def url(self):
        return f'https://www.iqiyi.com/{self.bangumi_id}.html'


class IqiyiEpisode(S.BgmIpViewer):
    name = 'iqiyi'

    class Meta:
        table_name = 'ep_iqiyi'

    source_ep_id = pw.CharField(primary_key=True)
    ep_id = pw.IntegerField()
    subject_id = pw.IntegerField()
    title = pw.CharField(default='')

    @property
    def url(self):
        return f'https://www.iqiyi.com/{self.source_ep_id}.html'


if __name__ == '__main__':  # pragma: no cover
    from app.db.mysql import db

    with db.allow_sync():
        IqiyiEpisode.create_table()
        IqiyiBangumi.create_table()
