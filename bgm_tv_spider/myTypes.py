from typing import List

import scrapy.http
from parsel import SelectorList
from scrapy import Selector


def _xpath(self, query, namespaces=None, **kwargs) -> 'TypeSelectorList':
    pass


def _extract_first(self) -> str:
    pass


class MySelector(Selector):
    xpath = _xpath
    extract_first = _extract_first


class TypeSelectorList(SelectorList, List[MySelector]):
    extract_first = _extract_first


class TypeResponse(scrapy.http.TextResponse):
    xpath = _xpath
