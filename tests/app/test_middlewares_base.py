from unittest.mock import Mock

from fastapi import FastAPI
from starlette.requests import Request
from starlette.testclient import TestClient

from app.middlewares.http import setup_http_middleware


def test_logger_middleware():
    app = FastAPI(debug=False)
    setup_http_middleware(app)

    app.state.logger = Mock()

    @app.get("/raise")
    async def rai(request: Request):
        raise ValueError(233)

    with TestClient(app=app, raise_server_exceptions=False) as client:
        res = client.get("http://example/raise")
        assert res.status_code == 500
    app.state.logger.exception.assert_called_once()
