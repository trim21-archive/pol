import os
import secrets
from urllib.parse import urlencode

import pytz

DSN = os.getenv('DSN')

COMMIT_SHA = (os.getenv('COMMIT_SHA') or 'None')[:8]
TIMEZONE = pytz.timezone('Etc/GMT-8')

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DB')
DATABASE_URI = f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_DB = os.getenv('REDIS_DB', 0)

REDIS_URI = f'redis://{REDIS_HOST}/{REDIS_DB}'

HOST = os.environ.get('HOST', 'localhost:6001')
PROTOCOL = os.environ.get('PROTOCOL', 'http')

SECRET_KEY = (os.getenv('SECRET_KEY') or secrets.token_hex(32))[:32]
assert len(SECRET_KEY) == 32


class BgmTvAutoTracker:
    APP_ID = os.environ.get('BGM_TV_AUTO_TRACKER_APP_ID')
    APP_SECRET = os.environ.get('BGM_TV_AUTO_TRACKER_APP_SECRET')
    callback_url = '{}://{}/bgm-tv-auto-tracker/api.v0/oauth_callback'.format(
        PROTOCOL, HOST
    )
    oauth_url = 'https://bgm.tv/oauth/authorize?' + urlencode({
        'client_id': APP_ID,
        'response_type': 'code',
        'redirect_uri': callback_url,
    })
