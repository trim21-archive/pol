from typing import Dict, List, Optional

from pydantic import BaseModel


class Site(BaseModel):
    site: str
    id: Optional[str]
    begin: Optional[str]


class Item(BaseModel):
    title: str
    titleTranslate: Dict[str, List[str]]
    type: str
    lang: str
    officialSite: str
    begin: str
    end: str
    sites: List[Site]

    @property
    def name_cn(self):
        return self.titleTranslate.get("zh-Hans", [self.title])[0]


class BangumiData(BaseModel):
    items: List[Item]
