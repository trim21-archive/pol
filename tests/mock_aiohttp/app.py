import re
import datetime

import aioresponses

from app.services.bgm_tv.model import UserInfo, AuthResponse


def mock_bgm_auth_app(mock: aioresponses.aioresponses):
    def access_token_cb(url, data, **kwargs):
        assert 'code' in data
        assert 'client_id' in data
        assert 'grant_type' in data
        assert 'redirect_uri' in data
        assert 'client_secret' in data
        return aioresponses.CallbackResult(
            body=AuthResponse(
                access_token='access_token_example',
                expires_in=68400,
                token_type='access_token',
                scope=None,
                user_id=233,
                refresh_token='refresh_token_example'
            ).json(),
            headers={'Date': datetime.datetime.now().isoformat()},
        )

    def user_info_cb(url, **kwargs):
        return aioresponses.CallbackResult(
            body=UserInfo(
                id=2333,
                url=f'http://bgm.tv/user/{233}',
                username='233',
                nickname='nickname',
                avatar={
                    'large': 'http://lain.bgm.tv/pic/user/l/000/28/76/287622.jpg',
                    'medium': 'http://lain.bgm.tv/pic/user/m/000/28/76/287622.jpg',
                    'small': 'http://lain.bgm.tv/pic/user/s/000/28/76/287622.jpg?'
                },
                sign='hehe',
                usergroup=10
            ).json()
        )

    mock.post('https://bgm.tv/oauth/access_token', callback=access_token_cb)
    mock.get(
        re.compile(r'https://mirror.api.bgm.rin.cat/user/(.*)'), callback=user_info_cb
    )
