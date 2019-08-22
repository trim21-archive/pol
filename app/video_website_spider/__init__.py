from enum import Enum
from typing import Type
from urllib.parse import ParseResult, urlparse

from . import iqiyi, bilibili
from .base import BaseWebsite


class SupportWebsite(str, Enum):
    bilibili = 'bilibili'
    iqiyi = 'iqiyi'


class Dispatcher:
    def subject(self, subject_id: int, url: str):
        handler = self.dispatch(url)
        if handler:
            handler.valid_subject_url(url)
            handler.subject(subject_id, url)

    def ep(self, ep_id: int, url: str):
        handler = self.dispatch(url)
        if handler:
            handler.valid_ep_url(url)
            handler.ep(ep_id, url)

    def __init__(self):
        self.d = {
            SupportWebsite.bilibili: bilibili.Bilibili,
            SupportWebsite.iqiyi: iqiyi.Iqiyi,
        }

    def dispatch(self, url) -> Type[BaseWebsite]:
        u: ParseResult = urlparse(url)
        if u.hostname == 'www.bilibili.com':
            return self.get_handler(SupportWebsite.bilibili)
            # return self.d[SupportWebsite.bilibili]
        elif u.hostname == 'www.iqiyi.com':
            return self.get_handler(SupportWebsite.iqiyi)
            # return self.d[SupportWebsite.iqiyi]

    def get_handler(self, website):
        return self.d.get(website)


__all__ = ['iqiyi', 'bilibili', 'SupportWebsite', 'Dispatcher']
