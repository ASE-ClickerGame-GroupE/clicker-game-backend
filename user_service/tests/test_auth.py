import pytest
from datetime import timedelta
from user_service.app.auth import auth
from fastapi import HTTPException
from user_service.app.auth import routes
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from user_service.app.main import app
from user_service.app.db import get_db


def test_hash_and_verify_password():
    pwd = "secretpassword"
    hashed = auth.hash_password(pwd)

    assert hashed != pwd
    assert auth.verify_password(pwd, hashed) is True
    assert auth.verify_password("wrong", hashed) is False


def test_jwt_creation_and_decoding():
    data = {"sub": "testuser", "uuid": "123"}
    token = auth.create_access_token(data, expires_delta=timedelta(minutes=10))

    assert isinstance(token, str)

    decoded = auth.decode_access_token(token)
    assert decoded["sub"] == "testuser"
    assert decoded["uuid"] == "123"


def test_decode_invalid_token():
    res = auth.decode_access_token("invalid.token.here")
    assert res == {}


@pytest.mark.asyncio
async def test_signup_user_exists_error():

    mock_db = AsyncMock()
    # Mock find_one returning a user (meaning they exist)
    mock_db.users.find_one.return_value = {"loging": "existing"}

    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/auth/signup", json={"loging": "existing", "password": "p"})

    assert resp.status_code == 400
    assert "User already exists" in resp.text
    app.dependency_overrides = {}