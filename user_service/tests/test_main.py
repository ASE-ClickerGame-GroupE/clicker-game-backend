import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from user_service.app.main import app
from user_service.app.db import get_db


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_signup_route():
    # 1. Create the Mock DB
    mock_db = AsyncMock()
    # Mock find_one to return None (User doesn't exist yet)
    mock_db.users.find_one.return_value = None

    # 2. Override the dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # 3. Patch the create_user helper explicitly (since it's a function call, not a dependency)
    with patch("user_service.app.auth.routes.create_user", new=AsyncMock()) as mock_create:
        mock_create.return_value = {"user_id": "1", "loging": "new", "created_at": 0.0}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/auth/signup", json={"loging": "new", "password": "123"})

        assert resp.status_code == 200
        mock_create.assert_awaited_once()

    # 4. Clean up
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_login_route_success():
    mock_db = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    fake_user = {"user_id": "1", "loging": "u"}

    with patch("user_service.app.auth.routes.authenticate_user", new=AsyncMock(return_value=fake_user)):
        form_data = {"username": "u", "password": "p"}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/auth/token", data=form_data)

        assert resp.status_code == 200
        assert "access_token" in resp.json()

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_me_protected():
    fake_user_db = {"user_id": "1", "loging": "me", "created_at": 0.0}

    from user_service.app.auth.routes import get_current_user
    app.dependency_overrides[get_current_user] = lambda: fake_user_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/auth/me", headers={"Authorization": "Bearer fake"})

    assert resp.status_code == 200
    assert resp.json()["loging"] == "me"

    app.dependency_overrides = {}