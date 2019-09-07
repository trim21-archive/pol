from enum import Enum, IntEnum
from typing import Dict, List, Optional

from pydantic import BaseModel


class SubjectType(Enum):
    book = 1
    anime = 2
    music = 3
    game = 4
    real = 6


class SubjectImage(BaseModel):
    large: str
    common: str
    medium: str
    small: str
    grid: str


class EpisodeType(Enum):
    type0 = 0
    special = 1
    op = 2
    ed = 3
    ad = 4
    mad = 5
    other = 6


class StatusEnum(Enum):
    Air = 'Air'
    Today = 'Today'
    NA = 'NA'


class Episode(BaseModel):
    id: int
    url: str
    type: EpisodeType
    sort: int

    name: str
    name_cn: str
    duration: str
    airdate: str
    comment: int
    desc: str
    status: StatusEnum


class ApiSubject(BaseModel):
    id: int
    url: str
    type: SubjectType
    name: str
    name_cn: str
    summary: str
    air_date: str
    air_weekday: int
    images: SubjectImage
    eps: List[Episode]


class AuthResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: Optional[str]
    user_id: int
    refresh_token: str


class UserGroupEnum(IntEnum):
    admin = 1
    bangumi_admin = 2
    window_admin = 3
    quite_user = 4
    banned_user = 5
    character_admin = 8
    wiki_admin = 9
    normal_user = 10
    wiki = 11


class UserInfo(BaseModel):
    id: int
    url: str
    username: str
    nickname: str
    avatar: Dict[str, str]
    sign: str
    usergroup: UserGroupEnum


class RefreshResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: Optional[str] = ''
    refresh_token: str
