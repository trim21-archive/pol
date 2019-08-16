# import datetime
import asyncio
import logging
from copy import deepcopy
from typing import List, Optional
from asyncio import AbstractEventLoop
from logging import LogRecord
from datetime import datetime

import pytz
import msgpack
import aioredis
from aiologger.levels import LogLevel, check_level

from .base import Handler

# from .formatter import JsonFormatter


class LogstashHandler(Handler):
    def __init__(
        self,
        client,
        level: LogLevel = LogLevel.NOTSET,
        key='python-log',
        extra: dict = None,
        tz=pytz.utc,
        *,
        loop: Optional[AbstractEventLoop] = None,
    ) -> None:
        """
        Initializes the instance - basically setting the formatter to None
        and the filter list to empty.
        """
        super().__init__()
        self._level = check_level(level)
        self._loop: Optional[asyncio.AbstractEventLoop] = loop
        self.key = key
        self.client: aioredis.Redis = client
        self.packer = msgpack.Packer()
        if extra is None:
            self.extra = {}
        else:
            self.extra = extra
        self.tz = tz

        # def serialize(o: dict, **kwargs):
        #     o.update(self.extra)
        #     return json.dumps(o)
        # return self.packer.pack(o)

        # self.formatter = JsonFormatter(serializer=serialize)

    FIELD = frozenset(['event', 'kwargs', 'url', 'query', 'headers'])

    def format(self, record: LogRecord):
        serialized_time = datetime.fromtimestamp(record.created).astimezone(
            self.tz
        ).isoformat()
        o = deepcopy(self.extra)
        o.update({
            'msg': record.getMessage(),
            'logged_at': serialized_time,
            'line_number': record.lineno,
            'function': record.funcName,
            'level': logging.getLevelName(record.levelno),
            'file_path': record.pathname.replace('\\', '/'),
        })
        for field in self.FIELD:
            value = getattr(record, field, None)
            if value is not None:
                o[field] = value
        return self.packer.pack(o)

    async def store(self, record: List[bytes]):
        await self.client.rpush(self.key, *record)
