from typing import Tuple, Optional

import httpx

from app.core import config
from app.aio_services.utils import wrap_connection_error
from app.services.bgm_tv.model import UserInfo, UserCollection


class BgmApi:
    def __init__(self, mirror=False):
        if mirror:
            self.host = 'mirror.api.bgm.rin.cat'
        else:
            self.host = 'api.bgm.tv'

        self.session = httpx.Client(
            base_url=f'https://{self.host}/',
            headers={'user-agent': config.REQUEST_SERVICE_USER_AGENT},
        )

    @staticmethod
    def error_in_response(data: dict):
        return 'error' in data

    @wrap_connection_error
    async def get_user_watching_subjects(
        self, user_id: str
    ) -> Optional[Tuple[UserCollection]]:
        r = (
            await self.session.get(
                f'/user/{user_id}/collection',
                params={'cat': 'watching'},
            )
        ).json()

        if self.error_in_response(r):
            return None

        return tuple(UserCollection.parse_obj(x) for x in r)

    @wrap_connection_error
    async def get_user_info(self, user_id: str) -> Optional[UserInfo]:
        r = (await self.session.get(
            f'/user/{user_id}',
            params={'cat': 'watching'},
        )).json()
        if self.error_in_response(r):
            return None
        return UserInfo.parse_obj(r)


if __name__ == '__main__':  # pragma: no cover
    import asyncio

    async def main():
        print(await BgmApi().get_user_watching_subjects('1'))

    asyncio.run(main())
