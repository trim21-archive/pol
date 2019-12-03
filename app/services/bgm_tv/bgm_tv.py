from typing import Optional

import requests

from app.core import config
from app.services.bgm_tv.model import UserInfo, SubjectWithEps


class BgmApi:
    def __init__(self, mirror=False):
        self.session = requests.Session()
        if mirror:
            self.host = 'mirror.api.bgm.rin.cat'
            self.session.headers['user-agent'] = config.REQUEST_SERVICE_USER_AGENT
        else:
            self.host = 'api.bgm.tv'
            self.session.headers['user-agent'] = config.REQUEST_USER_AGENT

    def url(self, path):
        return f'https://{self.host}{path}'

    @staticmethod
    def error_in_response(data: dict):
        return 'error' in data

    def subject_eps(self, subject_id: int) -> Optional[SubjectWithEps]:
        r = self.session.get(self.url(f'/subject/{subject_id}/ep')).json()
        if self.error_in_response(r):
            return None
        return SubjectWithEps.parse_obj(r)

    def get_user_info(self, user_id: str) -> Optional[UserInfo]:
        r = self.session.get(self.url(f'/user/{user_id}')).json()
        if self.error_in_response(r):
            return None
        return UserInfo.parse_obj(r)

    def __del__(self):
        self.session.close()
