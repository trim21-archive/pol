import pytest
from fastapi import FastAPI

from app.depends import aiohttp_session


@pytest.mark.asyncio
async def test_aiohttp_session():
    app = FastAPI()
    app.state.client_session = object()
    assert app.state.client_session is await aiohttp_session(app=app)
