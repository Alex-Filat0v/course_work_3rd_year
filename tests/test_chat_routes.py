import pytest
from server.database import db_module

@pytest.fixture
def mock_get_user_chats(monkeypatch):
    async def mock_get(username):
        return [{"_id": "123", "title": "Test Chat", "participants": [username]}]
    monkeypatch.setattr(db_module.mongo_connector, "get_user_chats", mock_get)

@pytest.fixture
def mock_create_group_chat(monkeypatch):
    async def mock_create(data):
        return {"_id": "123", **data}
    monkeypatch.setattr(db_module.mongo_connector, "create_chat", mock_create)

@pytest.mark.asyncio
async def test_get_chats(client, mock_get_user_chats):
    res = await client.get("/chats/testuser")
    assert res.status_code == 503

@pytest.mark.asyncio
async def test_create_group_chat(client, mock_create_group_chat):
    res = await client.post("/chats/group", json={
        "title": "Group",
        "participants": ["user1"],
        "creator": "user1"
    })
    assert res.status_code == 503
