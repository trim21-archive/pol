import os.path
import secrets
from pathlib import Path
from urllib.parse import urlencode

import pytz
from starlette.config import Config

PROJ_ROOT = Path(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..")))

_config = Config(str(PROJ_ROOT / "env" / "dev"))

APP_NAME = "Pol server"

DEBUG = _config("DEBUG", cast=bool, default=False)

DSN = _config("DSN", default=None)

COMMIT_REF = _config("COMMIT_REF", default="dev")

TIMEZONE = pytz.timezone("Etc/GMT-8")

MYSQL_HOST = _config("MYSQL_HOST")
MYSQL_USER = _config("MYSQL_USER")
MYSQL_PASSWORD = _config("MYSQL_PASSWORD")
MYSQL_DB = _config("MYSQL_DB")
MYSQL_URI = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

REDIS_HOST = _config("REDIS_HOST")
REDIS_PASSWORD = _config("REDIS_PASSWORD")

REDIS_URI = f"redis://{REDIS_HOST}/0"

if REDIS_PASSWORD:
    REDIS_URI = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}/0"

VIRTUAL_HOST = _config("VIRTUAL_HOST", default="localhost:6001")
PROTOCOL = _config("PROTOCOL", default="http")

SECRET_KEY = (_config("SECRET_KEY", default=secrets.token_hex(32)))[:32]
assert len(SECRET_KEY) == 32

TESTING = _config("TESTING", default=False)


class BgmTvAutoTracker:
    APP_ID = _config("BGM_TV_AUTO_TRACKER_APP_ID")
    APP_SECRET = _config("BGM_TV_AUTO_TRACKER_APP_SECRET")
    callback_url = (
        f"{PROTOCOL}://{VIRTUAL_HOST}/bgm-tv-auto-tracker" f"/api.v1/oauth_callback"
    )
    oauth_url = "https://bgm.tv/oauth/authorize?" + urlencode(
        {"client_id": APP_ID, "response_type": "code", "redirect_uri": callback_url,}
    )


REQUEST_SERVICE_USER_AGENT = f"pol/{COMMIT_REF} https://github.com/trim21/pol"

REQUEST_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/78.0.3904.97 Safari/537.36"
)
