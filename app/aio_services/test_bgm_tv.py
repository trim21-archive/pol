import pytest

from app.aio_services import BgmApi
from app.services.bgm_tv.model import UserInfo, UserCollection

NON_EXIST_USER_ID = '1000000000'
EXIST_USER_ID = '1'


@pytest.fixture()
def bgm_api():
    yield BgmApi()


@pytest.mark.asyncio
async def test_get_user_watching_subjects_404(bgm_api: BgmApi):
    r = await bgm_api.get_user_watching_subjects(NON_EXIST_USER_ID)
    assert r is None, 'non exists user should return None'


@pytest.mark.asyncio
async def test_get_user_watching_subjects_200(bgm_api: BgmApi):
    r = await bgm_api.get_user_watching_subjects(EXIST_USER_ID)
    assert isinstance(r, tuple) and all(
        isinstance(x, UserCollection) for x in r
    ), 'get_user_info should return a UserCollection instance'


@pytest.mark.asyncio
async def test_get_user_info_404(bgm_api: BgmApi):
    r = await bgm_api.get_user_info(NON_EXIST_USER_ID)
    assert r is None, 'non exists user should return None'


@pytest.mark.asyncio
async def test_get_user_info_200(bgm_api: BgmApi):
    r = await bgm_api.get_user_info(EXIST_USER_ID)
    assert isinstance(r, UserInfo), 'get_user_info should return a UserInfo instance'
