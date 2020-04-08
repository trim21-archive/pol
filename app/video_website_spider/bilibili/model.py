from typing import Dict, List, Union

from pydantic import BaseModel


class Param(BaseModel):
    season_id: str


class Result(BaseModel):
    param: Param
    media_id: int


class BiliBiliApiResult(BaseModel):
    code: int
    message: str
    result: Result


class PlayerPageMediaInfo(BaseModel):
    id: int
    """
    ``mediaInfo.media_id``
    """

    ssId: int
    """
    ``mediaInfo.season_id``
    """
    title: str

    @property
    def media_id(self):
        return self.id

    @property
    def season_id(self):
        return self.ssId


class EpisodeType(BaseModel):
    aid: int
    badge: str
    badge_type: int
    cid: int
    cover: str
    id: int
    long_title: str
    share_url: str
    status: int
    title: str
    vid: str

    @property
    def index(self):
        return self.title

    @property
    def ep_id(self):
        return self.id


class OldPlayerPageEpInfo(BaseModel):
    index: str
    ep_id: int


class PlayerPageEpInfo(BaseModel):
    """
    schema of new player page
    don't have enough time to implement
    """

    id: int
    """
    ``epInfo.ep_id``
    """
    i: int
    """
    ``epInfo.index``
    """
    longTitle: str
    titleFormat: str

    @property
    def title(self):
        return self.titleFormat + " " + self.longTitle

    @property
    def ep_id(self):
        return self.id

    @property
    def index(self):
        return self.i + 1


class PlayerPageInitialState(BaseModel):
    mediaInfo: PlayerPageMediaInfo
    epInfo: PlayerPageEpInfo
    epList: List[PlayerPageEpInfo]


class BangumiPageSeason(BaseModel):
    media_id: int
    season_id: int


class BangumiPageMediaInfo(BaseModel):
    media_id: int
    title: str
    seasons: List[BangumiPageSeason]

    @property
    def season_id(self):
        for season in self.seasons:
            if season.media_id == self.media_id:
                return season.season_id


class BangumiPageMainSectionList(BaseModel):
    episodes: List[EpisodeType]
    id: int
    title: str


class BangumiPageInitialState(BaseModel):
    mediaInfo: BangumiPageMediaInfo
    mainSectionList: Union[BangumiPageMainSectionList, dict]

    @property
    def epList(self):
        return self.mainSectionList.episodes


class UnLoginPlayerPageSeason(BaseModel):
    is_new: int
    media_id: int
    season_id: int
    season_title: str
    title: str
    type: int


class UnLoginPlayerPageMediaInfo(BaseModel):
    param: Dict[str, str]
    seasons: List[UnLoginPlayerPageSeason]

    @property
    def season_id(self):
        return self.param["season_id"]

    @property
    def media_id(self):
        for item in self.seasons:
            if item.season_id == self.season_id:
                return item.media_id

    @property
    def title(self):
        for item in self.seasons:
            if item.season_id == self.season_id:
                return item.title


class UnLoginPlayerPageInitialState(BaseModel):
    mediaInfo: UnLoginPlayerPageMediaInfo


class SSPlayerPageMediaInfo(BaseModel):
    id: int
    ssId: int
    title: str

    @property
    def media_id(self):
        return self.id

    @property
    def season_id(self):
        return self.ssId


class SSPlayerPageInitialState(BaseModel):
    h1Title: str
    epList: List[dict]
