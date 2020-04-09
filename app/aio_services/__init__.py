from async_bgm_api import BgmApi

bgm_api = BgmApi()
bgm_api_mirror = BgmApi(mirror=True)

__all__ = ["bgm_api", "bgm_api_mirror"]
