import json
import re
from multiprocessing.pool import ThreadPool
from threading import Lock

import pymongo
import requests

from validators import InitialStateValidator

client = pymongo.MongoClient()
db = client.get_database('bilibili_bangumi')
collection = db.get_collection('episode_info')

regex = re.compile(
    r'<script>window\.__INITIAL_STATE__=({.*});\(function\(\){var s;\(s=document\.cu'
)

lock = Lock()
i = {'count': 0, 'all': db.get_collection('bilibili').find().count()}


def worker(media_id):
    # time.sleep(0.3)
    with lock:
        i['count'] = i['count'] + 1
        print('{}\n'.format(i['count'] / i['all']))
    r = requests.get(f'https://bangumi.bilibili.com/anime/{media_id}')
    x = regex.search(r.text)
    if not x:
        print(
            f'https://bangumi.bilibili.com/anime/{media_id} search result NoneType\n'
        )
        return
    json_text = x.group(1)
    if json_text:
        x = json.loads(json_text)
        x['epList'] = x['mediaInfo']['episodes']
        v = InitialStateValidator(x)
        if not v.is_valid():
            print(
                f'https://bangumi.bilibili.com/anime/{media_id} not valid {v.str_errors}\n'
            )
            return
        collection.update_one({
            '_id': v.validated_data['mediaInfo']['media_id']
        }, {'$set': v.validated_data},
                              upsert=True)
    else:
        print(f'https://bangumi.bilibili.com/anime/{media_id} not find json\n')


pool = ThreadPool(16)
pool.map(worker, [x['_id'] for x in db.get_collection('bilibili').find()])
