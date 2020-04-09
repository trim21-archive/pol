from enum import Enum
from typing import Any

from pydantic import BaseModel


class ResponseStatus(str, Enum):
    success = "success"
    warning = "warning"
    error = "error"


class CommonResponse(BaseModel):
    status: int
    data: Any
