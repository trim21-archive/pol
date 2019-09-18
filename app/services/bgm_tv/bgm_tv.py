from typing import Optional

import httpx

from app.services.bgm_tv.model import UserInfo, SubjectWithEps


class BgmApi:
    def __init__(self, mirror=False):
        if mirror:
            self.host = 'mirror.api.bgm.rin.cat'
        else:
            self.host = 'api.bgm.tv'
        self.session = httpx.Client(base_url=f'https://{self.host}')

    @staticmethod
    def error_in_response(data: dict):
        return 'error' in data

    def subject_eps(self, subject_id: int) -> Optional[SubjectWithEps]:
        r = self.session.get(f'/subject/{subject_id}/ep').json()
        if self.error_in_response(r):
            return None
        return SubjectWithEps.parse_obj(r)

    def get_user_info(self, user_id: str) -> Optional[UserInfo]:
        r = self.session.get(f'/user/{user_id}').json()
        if self.error_in_response(r):
            return None
        return UserInfo.parse_obj(r)
