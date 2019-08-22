from app.db_models import Ep, UserToken, BangumiSource, UserSubmitBangumi
from app.db.database import db
from app.db_models.iqiyi import IqiyiBangumi, IqiyiEpisode
from app.db_models.bilibili import BilibiliBangumi, BilibiliEpisode


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    'session start'
    db.set_allow_sync(True)
    UserToken.create_table()
    BangumiSource.create_table()
    UserSubmitBangumi.create_table()
    IqiyiEpisode.create_table()
    IqiyiBangumi.create_table()
    BilibiliEpisode.create_table()
    BilibiliBangumi.create_table()
    Ep.create_table()
