from starlette.testclient import TestClient


def test_get_subject_url(client: TestClient):
    r = client.get("/bgm.tv/api.v1/subject/player/927")
    assert r.status_code == 200, "subject with content should return 200"
    for item in r.json():
        if item["website"] == "bilibili":
            assert item["bangumi_id"] == "2688"
        if item["website"] == "iqiyi":
            assert item["bangumi_id"] == "a_19rrjze9o5"


# def test_get_subject_url_404(client: TestClient, ):
#     async def mock_get_current_user():
#         return sa.UserToken(user_id=233)
#
#     client.app.dependency_overrides[get_current_user] = mock_get_current_user
#     subject_id = 233593
#     url = 'https://www.bilibili.com/bangumi/play/ep262002'
#     with mock.patch('app.worker.submit_bangumi'):
#         r = client.put(f'/bgm.tv/api.v0/subject/player/{subject_id}',
#         json={'url': url})
#         assert r.status_code == 200, r.text
#         app.worker.submit_bangumi.delay.assert_called_once_with(subject_id, url)
#     assert r.status_code == 200, r.text
#
