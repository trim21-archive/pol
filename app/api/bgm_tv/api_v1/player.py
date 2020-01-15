from typing import List, Union

from fastapi import Depends, APIRouter
from pydantic import BaseModel
from databases import Database

from app.db_models import sa
from app.db.depends import get_db
from app.video_website_spider import SupportWebsite

router = APIRouter()


class PlayerSubject(BaseModel):
    website: SupportWebsite
    url: str
    bangumi_id: str


@router.get(
    '/subject/player/{subject_id}',
    description='针对bgm.tv的条目获取视频网站播放地址.',
    response_model=List[PlayerSubject],
)
async def get_player_url_of_subject(
    subject_id: int,
    db: Database = Depends(get_db),
):
    return [{
        'website': x.name,
        'bangumi_id': x.bangumi_id,
        'url': x.url,
    } for x in await get_all_bangumi_of_subject(db, subject_id)]


async def get_all_bangumi_of_subject(
    db: Database, subject_id: int
) -> List[Union[sa.BangumiBilibili, sa.BangumiIqiyi]]:
    bangumi_list = []
    for model in (sa.BangumiBilibili, sa.BangumiIqiyi):
        r = await db.fetch_one(sa.select([model]).where(model.subject_id == subject_id))
        if r:
            bangumi_list.append(model(**r))
    return bangumi_list
