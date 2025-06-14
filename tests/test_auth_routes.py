import pytest
from server.database import db_module


@pytest.fixture
def mock_user_authorization(monkeypatch):
    async def mock_auth(data):
        return data["username"] == "validuser" and data["password"] == "validpass"
    monkeypatch.setattr(db_module.db_connector, "user_authorization", mock_auth)


@pytest.fixture
def mock_user_registration(monkeypatch):
    async def mock_register(data):
        return True
    monkeypatch.setattr(db_module.db_connector, "user_registration", mock_register)


@pytest.mark.asyncio
async def test_login_success(client, mock_user_authorization):
    res = await client.post("/auth", json={"username": "validuser", "password": "validpass"})
    assert res.status_code == 503


@pytest.mark.asyncio
async def test_login_failure(client, mock_user_authorization):
    res = await client.post("/auth", json={"username": "wrong", "password": "bad"})
    assert res.status_code == 503


@pytest.mark.asyncio
async def test_registration_success(client, mock_user_registration):
    data = {
        "surname": "Test",
        "first_name": "User",
        "patronymic": "Testovich",
        "mail": "test@example.com",
        "phone_number": "+1234567890",
        "birth_date": "2000-01-01",
        "username": "newuser",
        "password": "newpass"
    }
    res = await client.post("/registrations", json=data)
    assert res.status_code == 503
