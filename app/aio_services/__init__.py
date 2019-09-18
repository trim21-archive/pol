from .bgm_tv import BgmApi
from .exceptions import ServerConnectionError

bgm_api = BgmApi()
bgm_api_mirror = BgmApi(mirror=True)

__all__ = ['bgm_api', 'ServerConnectionError', 'bgm_api_mirror']
