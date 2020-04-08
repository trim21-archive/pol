import json
import asyncio
import pathlib
from os import path
from typing import List
from collections import defaultdict

import aiohttp
import aioredis
from pydantic import ValidationError
from sqlalchemy.dialects.mysql import insert

from app.core import config
from app.db.mysql import database
from app.db.utils import preserve_fields
from app.db_models import sa
from app.video_website_spider import SupportWebsite
from data_manager.models.bangumi_data import Item

base_dir = pathlib.Path(path.dirname(__file__))


async def save_bangumi_data_to_db(redis):
    container = defaultdict(list)
    data: List[Item] = []
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://cdn.jsdelivr.net/npm/bangumi-data@0.3.x/dist/data.json"
        ) as response:
            server_data = await response.json()

        for item in server_data["items"]:
            try:
                data.append(Item.parse_obj(item))
            except ValidationError as e:
                print(item)
                print(e)

        for item in data:
            site_bangumi = [site for site in item.sites if site.site == "bangumi"]

            if site_bangumi:
                site_bangumi = site_bangumi[0]
            else:
                continue

            subject_id = int(site_bangumi.id)

            for site in item.sites:
                if not site.id:
                    continue
                if site.site == SupportWebsite.bilibili:
                    try:
                        container[SupportWebsite.bilibili].append(
                            {
                                "subject_id": subject_id,
                                "media_id": int(site.id),
                                "season_id": await get_season_id(
                                    redis, session, site.id
                                ),
                                "title": item.name_cn,
                            }
                        )
                    except KeyError:
                        pass
                elif site.site == SupportWebsite.iqiyi:
                    container[SupportWebsite.iqiyi].append(
                        {
                            "subject_id": subject_id,
                            "bangumi_id": site.id,
                            "title": item.name_cn,
                        }
                    )

    for key, value in container.items():
        print(key, len(value))

    # print(len(container[SupportWebsite.bilibili]))
    await insert_bilibili_bangumi(database, container[SupportWebsite.bilibili])
    await insert_iqiyi_bangumi(database, container[SupportWebsite.iqiyi])


async def save_patch_to_db():
    with open(base_dir / "patch.json", encoding="utf-8") as f:
        d = json.load(f)

    await insert_bilibili_bangumi(
        database,
        [
            {
                "subject_id": int(x["subject_id"]),
                "media_id": x["season_id"],
                "season_id": x["season_id"],
                "title": x.get("title", ""),
            }
            for x in d[SupportWebsite.bilibili]
        ],
    )

    await insert_iqiyi_bangumi(
        database,
        [
            {
                "subject_id": int(x["subject_id"]),
                "bangumi_id": x["bangumi_id"],
                "title": x.get("title", ""),
            }
            for x in d[SupportWebsite.iqiyi]
        ],
    )


async def insert_bilibili_bangumi(db, values):
    insert_stmt = insert(sa.BangumiBilibili)
    query = insert_stmt.on_duplicate_key_update(
        **preserve_fields(insert_stmt, "title", "season_id", "media_id"),
    )
    await db.execute_many(query, values)


async def insert_iqiyi_bangumi(db, values):
    insert_stmt = insert(sa.BangumiIqiyi)
    query = insert_stmt.on_duplicate_key_update(
        **preserve_fields(insert_stmt, "title", "bangumi_id"),
    )
    await db.execute_many(query, values)


async def get_season_id(
    redis_client: aioredis.Redis, session: aiohttp.ClientSession, media_id,
):
    r = await redis_client.get(f"bilibili:initial_state:media_id:{media_id}")
    if r:
        return int(r)
    async with session.get(
        f"https://bangumi.bilibili.com/view/web_api/media?media_id={media_id}"
    ) as r:
        season_id = (await r.json())["result"]["param"]["season_id"]
    await redis_client.set(
        f"bilibili:initial_state:media_id:{media_id}", str(season_id)
    )
    return season_id


async def main():
    redis_client = await aioredis.create_redis_pool(
        address=config.REDIS_URI, password=config.REDIS_PASSWORD,
    )
    await database.connect()
    await asyncio.gather(save_bangumi_data_to_db(redis_client), save_patch_to_db())
    await database.disconnect()


if __name__ == "__main__":  # pragma: no cover
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print("exit")
