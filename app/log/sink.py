from copy import deepcopy
from typing import Any, Dict

import pytz
import redis
import msgpack


class Sink:

    FIELD = frozenset(["event", "kwargs", "url", "query", "headers", "exception"])

    def __init__(
        self, client, *, key="python-log", extra: dict = None, tz=pytz.utc,
    ) -> None:
        """
        Initializes the instance - basically setting the formatter to None
        and the filter list to empty.
        """
        super().__init__()
        self.key = key
        self.client: redis.StrictRedis = client
        self.packer = msgpack.Packer()
        if extra is None:
            self.extra: Dict[str, Any] = {}
        else:
            self.extra = extra
        self.tz = tz

    def __call__(self, record):
        message = self.format(record)
        self.client.rpush(self.key, message)

    def format(self, record):
        body = str(record)
        record = record.record
        serialized_time = record["time"].astimezone(self.tz).isoformat()
        o = deepcopy(self.extra)
        o.update(
            {
                "body": body,
                "msg": record["message"],
                "logged_at": serialized_time,
                "line_number": record["line"],
                "function": record["function"],
                "level": record["level"].name,
                "module": record["name"],
                "process": record["process"].id,
                "thread": record["thread"].id,
            }
        )
        for field in self.FIELD:
            value = record["extra"].get(field)
            if value is not None:
                o[field] = value
        return self.packer.pack(o)
