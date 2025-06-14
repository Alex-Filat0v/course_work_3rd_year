import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from server.routes.auth_routes import auth_router
from server.routes.chat_routes import chat_router
from server.routes.user_routes import user_router
from server.routes.websocket_routes import ws_router

import pytest_asyncio

@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(user_router)
    app.include_router(ws_router)
    return app


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(base_url="http://test") as ac:
        yield ac
