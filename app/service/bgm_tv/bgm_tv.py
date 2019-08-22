import requests

from app.service.bgm_tv.model import ApiSubject


class BgmApi:
    def __init__(self):
        self.session = requests.Session()

    def subject_eps(self, subject_id: int) -> ApiSubject:
        return ApiSubject.parse_raw(
            self.session.get(f'https://api.bgm.tv/subject'
                             f'/{subject_id}/ep').text
        )
