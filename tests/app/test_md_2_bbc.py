from starlette.testclient import TestClient

import app.fast
import app.md2bbc

client = TestClient(app.fast.app)


def test_html_view():
    response = client.get('/md2bbc')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
