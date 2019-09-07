from fastapi.security.api_key import APIKeyCookie, APIKeyHeader

API_KEY_NAME = 'api_key'

cookie_scheme = APIKeyCookie(name='bgm-tv-auto-tracker', auto_error=False)
API_KEY_HEADER = APIKeyHeader(name='api-key', auto_error=False)
API_KEY_COOKIES = APIKeyCookie(name='api-key', auto_error=False)
