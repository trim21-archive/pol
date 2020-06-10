from typing import Any, Type

import orjson
from starlette.responses import Response, JSONResponse


class CalendarResponse(Response):
    media_type = "text/calendar"


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(content)


def response(
    model: Type = None, description: str = None, headers=None, cls: Type = None
):
    if model is None:
        d = {}
    else:
        d = {"model": model}
    if description:
        d["description"] = description
    if headers is not None:
        d["headers"] = headers
    if cls is not None:
        d["response_class"] = cls
    return d


def header(t: Type = None, description: str = ""):
    d = {}
    if t is not None:
        d = {"schema": {"type": _type_map(t)}}
    if description:
        d["description"] = description
    return d


def _type_map(t) -> str:
    if t is int:
        return "integer"
    elif t is str:
        return "string"
    return t
