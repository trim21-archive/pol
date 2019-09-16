from .bgm_tv import BgmApi
from .exceptions import ServerConnectionError

bgm_api = BgmApi()

__all__ = ['bgm_api', 'ServerConnectionError']
