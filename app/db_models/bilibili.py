import peewee as pw

from app.db_models.base import S


class BilibiliBangumi(S.BgmIpViewer):
    """
    db table for bilibili bangumi
    """
    name = 'bilibili'

    class Meta:
        table_name = 'bangumi_bilibili'

    subject_id = pw.IntegerField(primary_key=True)

    media_id = pw.IntegerField(index=True)
    season_id = pw.IntegerField(default=0)
    title = pw.CharField(default='')

    @property
    def bangumi_id(self):
        return self.season_id

    @property
    def url(self):
        return f'https://www.bilibili.com/bangumi/media/md{self.media_id}/'


class BilibiliEpisode(S.BgmIpViewer):
    name = 'bilibili'

    class Meta:
        table_name = 'ep_bilibili'

    source_ep_id = pw.IntegerField(primary_key=True)
    ep_id = pw.IntegerField()
    subject_id = pw.IntegerField()
    title = pw.CharField(default='')

    @property
    def url(self):
        return f'https://www.bilibili.com/bangumi/play/ep{self.source_ep_id}'


if __name__ == '__main__':  # pragma: no cover
    pass

    BilibiliBangumi.create_table()
    BilibiliEpisode.create_table()
