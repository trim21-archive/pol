import httpx


class ServerConnectionError(Exception):
    def __init__(
        self,
        request: httpx.Request = None,
        response: httpx.Response = None,
        raw_exception: Exception = None,
    ):
        self.request = request
        self.response = response
        self.raw = raw_exception
