import pytest_mock
from starlette.testclient import TestClient

import app.fast
import app.md2bbc

client = TestClient(app.fast.app)


def test_html_view():
    response = client.get('/md2bbc')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']


def test_convert_api(mocker: pytest_mock.MockFixture):
    with mocker.patch('app.md2bbc.markdown2bbcode', return_value='[b]b[/b]'):
        response = client.post(
            '/md2bbc',
            data={'markdown': '**b**'},
        )
        assert response.status_code == 200
        assert response.text == '[b]b[/b]'
        assert 'text/plain' in response.headers['content-type']
        app.md2bbc.markdown2bbcode.assert_called_once_with('**b**')
