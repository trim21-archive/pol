# import pytest
# from starlette.testclient import TestClient
#
# from app import db_models
# from app.db.mysql import objects
# from app.db_models import UserToken, UserSubmitBangumi
# from app.api.auth.api_v1.depends import get_current_user

# def test_submit_subject_id_require_auth(client: TestClient):
#     r = client.post(
#         '/bgm-tv-auto-tracker/api.v1/submit/subject_id',
#         json={
#             'bangumi_id': 'string',
#             'source': 'bilibili',
#             'subject_id': 288,
#         }
#     )
#     assert r.status_code == 403, "user submit subject_id don't need auth"
#
#
# def test_submit_subject_id(client: TestClient):
#     async def mock_get_current_user():
#         return UserToken(user_id=233)
#
#     client.app.dependency_overrides[get_current_user] = mock_get_current_user
#
#     r = client.post(
#         '/bgm-tv-auto-tracker/api.v1/submit/subject_id',
#         json={
#             'bangumi_id': 'string',
#             'source': 'bilibili',
#             'subject_id': 288,
#         }
#     )
#     assert r.status_code == 200, r.text
#
#     with objects.allow_sync():
#         UserSubmitBangumi.get(
#             user_id=233, bangumi_id='string', source='bilibili', subject_id=288
#         )
#

#
# def test_submit_subject_id_bad_input(client: TestClient):
#     async def mock_get_current_user():
#         return UserToken(user_id=233)
#
#     client.app.dependency_overrides[get_current_user] = mock_get_current_user
#
#     r = client.post(
#         '/bgm-tv-auto-tracker/api.v1/submit/subject_id',
#         json={
#             'bangumi_id_': 'string',
#             'source': 'bilibili',
#             'subject_id': 288,
#         }
#     )
#     assert r.status_code == 422, r.text
#
#     with objects.allow_sync():
#         UserSubmitBangumi.get(
#             user_id=233, bangumi_id='string', source='bilibili', subject_id=288
#         )

#
# def test_submit_subject_id_exist(client: TestClient):
#     user_id = 233
#     subject_id = 2333
#     bangumi_id = 'b_id'
#     source = 'bilibili'
#
#     async def mock_get_current_user():
#         return UserToken(user_id=user_id)
#
#     client.app.dependency_overrides[get_current_user] = mock_get_current_user
#     with objects.allow_sync():
#         db_models.BangumiSource.replace(
#             source=source,
#             bangumi_id=bangumi_id,
#             subject_id=subject_id,
#         ).execute()
#     r = client.post(
#         '/bgm-tv-auto-tracker/api.v1/submit/subject_id',
#         json={
#             'bangumi_id': bangumi_id,
#             'source': source,
#             'subject_id': subject_id,
#         }
#     )
#     assert r.status_code == 400, r.text
#     assert r.json()['detail'] == 'object already exists'
#     assert r.json()['status'] == 'error', 'submit existed object should return 400'
#
#     with pytest.raises(UserSubmitBangumi.DoesNotExist):
#         with objects.allow_sync():
#             UserSubmitBangumi.get(
#                 user_id=user_id,
#                 bangumi_id=bangumi_id,
#                 source=source,
#                 subject_id=subject_id,
#             )
#
#     with objects.allow_sync():
#         db_models.BangumiSource.delete().where(
#             db_models.BangumiSource.source == source,
#             db_models.BangumiSource.bangumi_id == bangumi_id,
#             db_models.BangumiSource.subject_id == subject_id,
#         ).execute()
