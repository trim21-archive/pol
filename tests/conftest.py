from app.db_models import UserToken, UserSubmitBangumi
from app.db.database import objects


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    'session start'
    with objects.allow_sync():
        UserToken.create_table()
        UserSubmitBangumi.create_table()
