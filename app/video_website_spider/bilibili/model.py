from typing import List

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
    @property
    def media_id(self):
        return self.id

    @property
    def season_id(self):
        return self.ssId


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
    episodes: List[OldPlayerPageEpInfo]

    @property
    def season_id(self):
        for season in self.seasons:
            if season.media_id == self.media_id:
                return season.season_id


class BangumiPageInitialState(BaseModel):
    mediaInfo: BangumiPageMediaInfo
    # mainSectionList: List[PlayerPageEpInfo]

    @property
    def epList(self):
        return self.mediaInfo.episodes

    # class Config(BaseModel.Config):
