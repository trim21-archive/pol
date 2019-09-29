import re
import datetime

import redis
import requests
import dateutil.parser
from bs4 import Tag, BeautifulSoup

from app.log import logger
from app.core import config
from app.services import bgm_tv
from app.db.database import objects
from app.aio_services import ServerConnectionError
from app.db_models.timeline import BgmTimeline

delta_time_pattern = re.compile(r'.*((\d+)分钟?)?((\d+)秒)?前.*')
REDIS_HASH_KEY = f'{config.APP_NAME}:user_id_map'

redis_client: redis.StrictRedis = redis.StrictRedis.from_url(config.REDIS_URI)

client = requests.Session()
client.headers['User-Agent'] = ' '.join((
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'AppleWebKit/537.36 (KHTML, like Gecko)',
    'Chrome/74.0.3729.169 Safari/537.36',
))

client.headers['accept'] = ','.join([
    'text/html',
    'application/xhtml+xml',
    'application/xml;q=0.9',
    'image/webp,image/apng,*/*;q=0.8',
    'application/signed-exchange;v=b3',
])

client.headers.setdefault('cache-control', 'max-age=0')
client.headers.setdefault('accept-language', 'zh-CN,zh;q=0.9')


@logger.catch()
def get():
    try:
        r = client.get('https://bangumi.tv/m/timeline')
    except requests.RequestException as e:
        logger.info('request exception ' + str(e))
        return
    now = dateutil.parser.parse(r.headers.get('date'))
    print('get timeline', now)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    parsed_timeline = []
    for li in soup.select('#timeline > ul > li'):
        li: Tag
        tml_id = li.attrs.get('id')
        info: Tag = li.find('span', class_='info clearit')

        user_name = get_user_name(info)
        user_id = 0

        date: Tag = (li.find('p', class_='date'))
        delta_time_str = date.decode_contents().strip()
        time = parse_time(delta_time_str, now)

        if user_name.isdecimal():
            user_id = user_name
        else:
            user_id_map_result = redis_client.hget(REDIS_HASH_KEY, user_name)
            if not user_id_map_result:
                try:
                    r = bgm_tv.server.get_user_info(user_name)
                except ServerConnectionError:
                    r = None
                if r:
                    redis_client.hset(REDIS_HASH_KEY, user_name, str(r.id))
                    user_id_map_result = r.id
                    user_id = int(user_id_map_result)
        parsed_timeline.append({
            'id': int(tml_id.split('_')[-1]),
            'user_name': user_name,
            'user_id': user_id,
            'time': int(time.timestamp()),
        })

    print(len(parsed_timeline))
    with objects.allow_sync():
        BgmTimeline.insert_many(parsed_timeline).on_conflict(
            preserve=(BgmTimeline.user_name, BgmTimeline.user_id, BgmTimeline.time)
        ).execute()


def get_user_name(info: Tag) -> str:
    user_parent = info.find('a', class_='l')
    may_be_user = user_parent.find('a', class_='l')
    if may_be_user:
        user: Tag = may_be_user
    else:
        user: Tag = user_parent
    user_id = user.attrs.get('href').split('/')[-1]

    return user_id


@logger.catch()
def parse_time(delta_time_str, now: datetime.datetime):
    result = delta_time_pattern.search(delta_time_str).groups()
    minute = int(result[1] or '0')
    second = int(result[3] or '0')
    delta = datetime.timedelta(minutes=minute, seconds=second)
    return now - delta


if __name__ == '__main__':
    get()
