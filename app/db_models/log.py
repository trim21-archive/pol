import peewee as pw

from app.db_models.base import S


class BangumiLog(S.BgmIpViewer):
    class Meta:
        table_name = 'bangumi_logs'

    subject_id = pw.IntegerField(primary_key=True)
    url = pw.CharField()
    user_id = pw.IntegerField()


class EpLog(S.BgmIpViewer):
    class Meta:
        table_name = 'ep_logs'

    ep_id = pw.IntegerField(primary_key=True)
    url = pw.CharField()
    user_id = pw.IntegerField()
