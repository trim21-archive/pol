import httpx

from app.services.bgm_tv.model import ApiSubject


class BgmApi:
    def __init__(self, mirror=False):
        self.session = httpx.Client()
        if mirror:
            self.host = 'mirror.api.bgm.rin.cat'
        else:
            self.host = 'api.bgm.tv'

    def subject_eps(self, subject_id: int) -> ApiSubject:

        return ApiSubject.parse_raw(
            self.session.get(f'https://{self.host}/subject/{subject_id}/ep', ).text
        )
