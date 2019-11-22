import mock

import app.worker
from app.worker import submit_ep, submit_bangumi
from app.core.celery_app import celery


@celery.task
def test_submit_bangumi():
    with mock.patch('app.worker.dispatcher'):
        submit_bangumi(2333, 'url233')
        app.worker.dispatcher.subject.assert_called_once_with(2333, 'url233')


@celery.task
def test_submit_ep():
    # dispatcher.ep(ep_id, url)
    with mock.patch('app.worker.dispatcher'):
        submit_ep(2333, 'url233')
        app.worker.dispatcher.ep.assert_called_once_with(2333, 'url233')
