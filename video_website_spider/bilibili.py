import re
import json
from urllib import parse

import requests
from pydantic import BaseModel


def get_ep_id_from_url(url: str):
    url_obj: parse.ParseResult = parse.urlparse(url)
    return url_obj.path.split('/')[-1].repalce('ep', '')


def get_bangumi_id_from_url(url: str):
    url_obj: parse.ParseResult = parse.urlparse(url)
    return url_obj.path.split('/')[-1].repalce('ep', '')


regex = re.compile(
    r'<script>window\.'
    r'__INITIAL_STATE__=({.*});'
    r'\(function\(\){var s;\(s=document\.cu'
)


def get_initial_state_from_html(html: str) -> dict:
    x = regex.search(html)
    json_text = x.group(1)
    if json_text:
        x = json.loads(json_text)
        return x


class MediaInfo(BaseModel):
    media_id: int
    season_id: int


class PlayerPageInitialState(BaseModel):
    mediaInfo: MediaInfo


def worker(media_id):
    r = requests.get(f'https://bangumi.bilibili.com/anime/{media_id}')
    initial_state = get_initial_state_from_html(r.text)
    if initial_state:
        return PlayerPageInitialState.parse_obj(initial_state)
