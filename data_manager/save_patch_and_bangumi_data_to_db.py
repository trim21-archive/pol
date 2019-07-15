import json
import pathlib
from os import path

import pydantic
import requests

from app.db import database
from app.db_models import BangumiSource
from data_manager.models.bangumi_data import Item

base_dir = pathlib.Path(path.dirname(__file__))

data_json = base_dir / '..' / 'bangumi-data' / 'dist' / 'data.json'

# if data_json.exists():
#     with data_json.open('r', encoding='utf-8') as f:
#         data = json.load(f)
# else:
data = []

for item in requests.get(
    'https://cdn.jsdelivr.net/npm/bangumi-data@0.3/dist/data.json'
).json()['items']:
    try:
        data.append(Item.parse_obj(item))
    except pydantic.ValidationError as e:
        print(item)
        print(e)


def save_bangumi_data_to_db():
    bangumi_data_item_list = []
    for item in data:
        d = {'title': item.titleTranslate.get('zh-Hans', None)}

        if not d['title']:
            d['title'] = item.title
        else:
            d['title'] = d['title'][0]

        site_bangumi = [site for site in item.sites if site.site == 'bangumi']

        if site_bangumi:
            site_bangumi = site_bangumi[0]
        else:
            continue

        subject_id = site_bangumi.id

        for site in item.sites:
            if site.site not in ['bilibili', 'iqiyi']:
                continue
            if not site.id:
                continue
            bangumi_data_item_list.append({
                'bangumi_id': site.id,
                'source': site.site,
                'subject_id': subject_id,
            })

    print(len(bangumi_data_item_list))
    BangumiSource.insert_many(bangumi_data_item_list).on_conflict(
        preserve=(BangumiSource.subject_id, )
    ).execute()


def save_patch_to_db():

    with open(base_dir / 'patch.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    patch_data_item_list = []
    for item in data:
        # for item in items:
        website = item['website']
        if item.get('subject_id'):
            subject_id = item['subject_id']
        elif item.get('subjectID'):
            subject_id = item['subjectID']
        else:
            subject_id = item['subject'].split('/')[-1]
        if item.get('bangumi_id'):
            bangumi_id = item['bangumi_id']
        elif item.get('bangumiID'):
            bangumi_id = item['bangumiID']
        else:
            raise ValueError('item has no bangumi id')
        patch_data_item_list.append({
            'bangumi_id': bangumi_id,
            'source': website,
            'subject_id': subject_id,
        })
        # MissingBangumi.delete().where(
        #     MissingBangumi.source == website,
        #     MissingBangumi.bangumi_id == bangumi_id,
        # ).execute()
    print(len(patch_data_item_list))
    BangumiSource.insert_many(patch_data_item_list).on_conflict(
        preserve=(BangumiSource.subject_id, )
    ).execute()


if __name__ == '__main__':
    with database.db.allow_sync():
        BangumiSource.create_table()
        # MissingBangumi.create_table()
        save_bangumi_data_to_db()
        save_patch_to_db()
    print('exit')
