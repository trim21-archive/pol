import pytest
from aioresponses import aioresponses

import app.db.mysql
from app.core import config
from app.db.mysql import db


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    'session start'
    db.set_allow_sync(True)
    if config.TEST:
        app.db.mysql.database.options['force_rollback'] = True


@pytest.fixture
def mock_aiohttp():
    with aioresponses() as m:
        yield m
