import httpx

http_client = httpx.Client()
h11_client = httpx.Client(http_versions=['HTTP/1.1'])
