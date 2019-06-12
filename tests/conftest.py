from app.db_models import UserToken
from app.db.database import objects


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    with objects.allow_sync():
        UserToken.create_table()
