import os

import mock
import pytest

from etc.gunicorn import get_worker


@pytest.mark.parametrize('count', range(1, 10))
def test_worker_count(count: int):
    with mock.patch('multiprocessing.cpu_count') as m:
        m.return_value = count
        assert get_worker() == count * 2 + 1


def test_worker_count_gt_0():
    with mock.patch('multiprocessing.cpu_count') as m:
        m.return_value = -1
        with pytest.raises(AssertionError):
            get_worker()


@pytest.mark.parametrize('count', range(1, 10))
def test_worker_count_by_env(count: int):
    with mock.patch.dict(os.environ, {'WEB_CONCURRENCY': str(count)}):
        assert get_worker() == count, 'get worker number by env'
