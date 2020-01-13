import pytest
from aioresponses import aioresponses

from app.db.mysql import database


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    'session start'
    database.options['force_rollback'] = True


@pytest.fixture
def mock_aiohttp():
    with aioresponses() as m:
        yield m
