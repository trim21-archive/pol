from starlette.testclient import TestClient


def test_query_subject_id_iqiyi(client: TestClient):
    r = client.get(
        '/bgm-tv-auto-tracker/api.v1/subject_id',
        params={
            'bangumi_id': 'a_19rrhuee75',
            'source': 'iqiyi',
        }
    )
    assert r.status_code == 200
    assert r.json()['subject_id'] == 12, 'iqiyi bangumi subject_id not match' + r.text


def test_query_subject_id_bilibili(client: TestClient):
    r = client.get(
        '/bgm-tv-auto-tracker/api.v1/subject_id',
        params={
            'bangumi_id': '25210',
            'source': 'bilibili',
        }
    )
    assert r.status_code == 200
    assert r.json(
    )['subject_id'] == 290, 'bilibili bangumi subject_id not match ' + r.text


def test_query_subject_id_error(client: TestClient):
    r = client.get(
        '/bgm-tv-auto-tracker/api.v1/subject_id',
        params={
            'bangumi_id': 'string',
            'source': 'no',
        }
    )
    assert r.status_code == 422, "user submit subject_id don't need auth"
