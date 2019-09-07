import json
import pathlib
from os import path
from collections import defaultdict

import pydantic

from app.db import database
from app.client import http_client
from app.db_models.iqiyi import IqiyiBangumi
from app.db_models.bilibili import BilibiliBangumi
from app.video_website_spider import SupportWebsite
from data_manager.models.bangumi_data import Item
from app.video_website_spider.bilibili.model import PlayerPageInitialState
from app.video_website_spider.bilibili.bilibili import get_initial_state_from_html

base_dir = pathlib.Path(path.dirname(__file__))


def save_bangumi_data_to_db():
    container = defaultdict(list)
    data = []
    for item in http_client.get(
        'https://cdn.jsdelivr.net/npm/bangumi-data@0.3.x/dist/data.json'
    ).json()['items']:
        try:
            data.append(Item.parse_obj(item))
        except pydantic.ValidationError as e:
            print(item)
            print(e)

    for item in data:
        site_bangumi = [site for site in item.sites if site.site == 'bangumi']

        if site_bangumi:
            site_bangumi = site_bangumi[0]
        else:
            continue

        subject_id = int(site_bangumi.id)

        for site in item.sites:
            if not site.id:
                continue
            if site.site == SupportWebsite.bilibili:
                container[SupportWebsite.bilibili].append({
                    'subject_id': subject_id,
                    'media_id': int(site.id),
                })
            elif site.site == SupportWebsite.iqiyi:
                container[SupportWebsite.iqiyi].append({
                    'subject_id': subject_id,
                    'bangumi_id': site.id,
                })
    # print(l[SupportWebsite.iqiyi])
    for key, value in container.items():
        print(key, len(value))
    # print(len(set([x['subject_id'] for x in l[SupportWebsite.iqiyi]])))
    # print(len(set([x['bangumi_id'] for x in l[SupportWebsite.iqiyi]])))
    # print(l[SupportWebsite.bilibili])
    BilibiliBangumi.insert_many(
        container[SupportWebsite.bilibili]
    ).on_conflict(preserve=[BilibiliBangumi.media_id]).execute()

    IqiyiBangumi.insert_many(
        container[SupportWebsite.iqiyi]
    ).on_conflict(preserve=(IqiyiBangumi.bangumi_id, )).execute()


def save_patch_to_db():
    with open(base_dir / 'patch.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
    IqiyiBangumi.insert_many(
        [{
            'subject_id': int(x['subject_id']),
            'bangumi_id': x['bangumi_id'],
        } for x in d[SupportWebsite.iqiyi]]
    ).on_conflict(preserve=(IqiyiBangumi.bangumi_id, )).execute()
    # for item in d[SupportWebsite.bilibili]:
    #     if 'media_id' in item and item['media_id'] != 1:
    #         continue
    #     item['season_id'] = item['bangumi_id']
    #     item['media_id'] = get_media_id(item['season_id'])
    #     with open(base_dir / 'patch.json', 'w', encoding='utf-8') as f:
    #         json.dump(d, f, ensure_ascii=False, indent=2)
    BilibiliBangumi.insert_many(
        [{
            'subject_id': x['subject_id'],
            'media_id': x['media_id'],
            'season_id': x['season_id'],
        } for x in d[SupportWebsite.bilibili] if x['media_id'] != 1]
    ).on_conflict(preserve=(BilibiliBangumi.season_id, )).execute()


def get_media_id(season_id):
    r = http_client.get(f'https://www.bilibili.com/bangumi/play/ss{season_id}/')
    state = get_initial_state_from_html(r.text)
    if not state:
        print(r.url)
        return 1
    state = PlayerPageInitialState.parse_obj(state)
    return state.mediaInfo.media_id


if __name__ == '__main__':
    with database.db.allow_sync():
        # BangumiSource.create_table()
        # MissingBangumi.create_table()
        save_bangumi_data_to_db()
        save_patch_to_db()
        # db.commit()
    print('exit')
