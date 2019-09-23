import os.path
import secrets
from pathlib import Path
from urllib.parse import urlencode

import pytz
from starlette.config import Config

PROJ_ROOT = Path(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

config = Config(PROJ_ROOT / 'env' / 'dev')

APP_NAME = 'Pol server'

DEBUG = config('DEBUG', cast=bool, default=False)

DSN = config('DSN', default=None)

COMMIT_TAG = config('COMMIT_TAG', default=None)
COMMIT_SHA = config('COMMIT_SHA', default='None')[:8]
COMMIT_REV = COMMIT_TAG or COMMIT_SHA or ''

TIMEZONE = pytz.timezone('Etc/GMT-8')

MYSQL_HOST = config('MYSQL_HOST')
MYSQL_USER = config('MYSQL_USER')
MYSQL_PASSWORD = config('MYSQL_PASSWORD')
MYSQL_DB = config('MYSQL_DB')
DATABASE_URI = f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'

REDIS_HOST = config('REDIS_HOST')
REDIS_PASSWORD = config('REDIS_PASSWORD')

REDIS_URI = f'redis://{REDIS_HOST}/0'

if REDIS_PASSWORD:
    REDIS_URI = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}/0'

RABBITMQ_ADDR = config('RABBITMQ_ADDR')
RABBITMQ_USER = config('RABBITMQ_USER')
RABBITMQ_PASS = config('RABBITMQ_PASS')

VIRTUAL_HOST = config('VIRTUAL_HOST', default='localhost:6001')
PROTOCOL = config('PROTOCOL', default='http')

SECRET_KEY = (config('SECRET_KEY', default=secrets.token_hex(32)))[:32]
assert len(SECRET_KEY) == 32


class BgmTvAutoTracker:
    APP_ID = config('BGM_TV_AUTO_TRACKER_APP_ID')
    APP_SECRET = config('BGM_TV_AUTO_TRACKER_APP_SECRET')
    callback_url = (
        f'{PROTOCOL}://{VIRTUAL_HOST}/bgm-tv-auto-tracker'
        f'/api.v1/oauth_callback'
    )
    oauth_url = 'https://bgm.tv/oauth/authorize?' + urlencode({
        'client_id': APP_ID,
        'response_type': 'code',
        'redirect_uri': callback_url,
    })
