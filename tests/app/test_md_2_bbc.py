import mock
from starlette.testclient import TestClient

import app.fast
import app.md2bbc

client = TestClient(app.fast.app)


def test_html_view():
    response = client.get('/md2bbc')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']


def test_convert_api():
    response = client.post(
        '/md2bbc',
        data={'markdown': '**b** *i*'},
    )
    assert response.status_code == 200
    assert response.text.strip() == '[b]b[/b] [i]i[/i]'
    assert 'text/plain' in response.headers['content-type']


def test_call_api():
    with mock.patch('app.md2bbc.markdown2bbcode', return_value='[i]b[/i]') as mocker:
        response = client.post(
            '/md2bbc',
            data={'markdown': '*b*'},
        )
        assert response.status_code == 200
        assert response.text.strip() == '[i]b[/i]'
        assert 'text/plain' in response.headers['content-type']
        mocker.assert_called_once_with('*b*')
