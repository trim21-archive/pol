import abc
import urllib.parse
from typing import Dict

from sentry_sdk.utils import transaction_from_function


class Middleware(metaclass=abc.ABCMeta):
    def __init__(self, app):
        self.app = app

    @abc.abstractmethod
    async def __call__(self, scope, receive, send):
        raise NotImplementedError()  # pragma: no cover

    # below functions come from ``sentry_sdk.integrations.asgi.SentryAsgiMiddleware``
    @staticmethod
    def get_url(scope):
        """
        Extract URL from the ASGI scope, without also including the querystring.
        """
        scheme = scope.get('scheme', 'http')
        server = scope.get('server', None)
        path = scope.get('root_path', '') + scope['path']

        for key, value in scope['headers']:
            if key == b'host':
                host_header = value.decode('latin-1')
                return f'{scheme}://{host_header}{path}'

        if server is not None:
            host, port = server
            default_port = {'http': 80, 'https': 443, 'ws': 80, 'wss': 443}[scheme]
            if port != default_port:
                return f'{scheme}://{host}:{port}{path}'
            return f'{scheme}://{host}{path}'
        return path

    @staticmethod
    def get_query(scope):
        return urllib.parse.unquote(scope['query_string'].decode('latin-1'))

    @staticmethod
    def get_headers(scope):
        headers: Dict[str, str] = {}
        for raw_key, raw_value in scope['headers']:
            key = raw_key.decode('latin-1')
            value = raw_value.decode('latin-1')
            if key in headers:
                headers[key] = headers[key] + ', ' + value
            else:
                headers[key] = value
        return headers

    @staticmethod
    def get_transaction(scope):
        return transaction_from_function(scope['endpoint'])
