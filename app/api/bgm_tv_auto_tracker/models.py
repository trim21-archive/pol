from typing import Any, Dict, List

from pydantic import BaseModel


class MediaInfo(BaseModel):
    actors: str
    alias: str
    areas: List[Dict[str, Any]]
    media_id: int
    mode: int
    season_id: int
    season_status: int
    series_title: str
    title: str
    total_ep: int
    link: str


class EpInfo(BaseModel):
    aid: int
    cid: int
    ep_id: int
    index: str
    index_title: str
    mid: int
    section_id: int
    section_type: int
    vid: str


class BiliBiliSubmitInfo(BaseModel):
    mediaInfo: MediaInfo
    epInfo: EpInfo
    epList: List[EpInfo]
