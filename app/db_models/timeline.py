import peewee as pw

from app.db_models.base import S


class BgmTimeline(S.BgmIpViewer):
    class Meta:
        table_name = 'bgm_timeline'

    id = pw.BigIntegerField(primary_key=True)
    user_name = pw.CharField(index=True)
    user_id = pw.IntegerField(index=True, default=0)
    time = pw.IntegerField(index=True)
