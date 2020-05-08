from unittest import mock

import pytest

import app.worker
from app.worker import submit_ep, submit_bangumi

_re_run = 3


@pytest.mark.flaky(reruns=_re_run)
# @celery.task
def test_submit_bangumi():
    with mock.patch("app.worker.dispatcher"):
        submit_bangumi(2333, "url233")
        app.worker.dispatcher.subject.assert_called_once_with(2333, "url233")


@pytest.mark.flaky(reruns=_re_run)
# @celery.task
def test_submit_ep():
    # dispatcher.ep(ep_id, url)
    with mock.patch("app.worker.dispatcher"):
        submit_ep(2333, "url233")
        app.worker.dispatcher.ep.assert_called_once_with(2333, "url233")
