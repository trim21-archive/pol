import pytest

from app.services.bgm_tv import BgmApi
from app.services.bgm_tv.model import UserInfo, SubjectWithEps

NON_EXIST_USER_ID = "1000000000"
NON_EXIST_SUBJECT_ID = 1000000000
EXIST_USER_ID = "1"
EXIST_SUBJECT_ID = 8

_re_run = 3


@pytest.fixture()
def bgm_api():
    with BgmApi(mirror=True) as b:
        yield b


@pytest.mark.flaky(reruns=_re_run)
def test_subject_eps_404(bgm_api: BgmApi):
    r = bgm_api.subject_eps(NON_EXIST_SUBJECT_ID)
    assert r is None, "non exists subject should return None"


@pytest.mark.flaky(reruns=_re_run)
def test_subject_eps_200(bgm_api: BgmApi):
    r = bgm_api.subject_eps(EXIST_SUBJECT_ID)
    assert isinstance(
        r, SubjectWithEps
    ), "subject_eps should return a SubjectWithEps instance"


@pytest.mark.flaky(reruns=_re_run)
def test_get_user_info_404(bgm_api: BgmApi):
    r = bgm_api.get_user_info(NON_EXIST_USER_ID)
    assert r is None, "non exists user should return None"


@pytest.mark.flaky(reruns=_re_run)
def test_get_user_info_200(bgm_api: BgmApi):
    r = bgm_api.get_user_info(EXIST_USER_ID)
    assert isinstance(r, UserInfo), "get_user_info should return a UserInfo instance"
