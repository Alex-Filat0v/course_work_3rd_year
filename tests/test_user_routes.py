import pytest
from server.database import db_module


@pytest.fixture
def mock_search_users(monkeypatch):
    async def mock_search(query, current_user):
        return [{"username": "someone", "first_name": "Some", "surname": "One"}]
    monkeypatch.setattr(db_module.db_connector, "search_users", mock_search)


@pytest.fixture
def mock_get_contacts(monkeypatch):
    async def mock_contacts(username):
        return [{"username": "friend", "first_name": "Friend", "surname": "User"}]
    monkeypatch.setattr(db_module.db_connector, "get_contacts", mock_contacts)


@pytest.mark.asyncio
async def test_search_for_users(client, mock_search_users):
    res = await client.get("/users/search", params={"query": "so", "current_user": "me"})
    assert res.status_code == 503


@pytest.mark.asyncio
async def test_get_user_contacts(client, mock_get_contacts):
    res = await client.get("/contacts/me")
    assert res.status_code == 503
