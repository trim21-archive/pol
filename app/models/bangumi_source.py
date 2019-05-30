from enum import Enum

from pydantic import BaseModel


class BangumiSourceEnum(str, Enum):
    bilibili = 'bilibili'
    iqiyi = 'iqiyi'


class BangumiSource(BaseModel):
    source: BangumiSourceEnum
    bangumi_id: str
    subject_id: int
