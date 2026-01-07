import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from user_service.app import crud
from user_service.app.models import UserCreate, UserInDB


@pytest.mark.asyncio
async def test_create_user():
    mock_db = MagicMock()
    mock_db.users = MagicMock()
    mock_db.users.insert_one = AsyncMock()

    user_in = UserCreate(loging="test", password="123", email="t@t.com")

    user_out = await crud.create_user(mock_db, user_in)

    assert user_out.loging == "test"
    assert hasattr(user_out, "user_id")
    mock_db.users.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_found():
    mock_db = MagicMock()
    mock_db.users = MagicMock()
    # Simulate DB returning a doc
    mock_db.users.find_one = AsyncMock(return_value={
        "user_id": "u1", "loging": "test", "email": None,
        "created_at": 1.0, "password": "hash"
    })

    user = await crud.get_user(mock_db, "u1")
    assert user.user_id == "u1"
    assert not hasattr(user, "password")  # Should be popped


@pytest.mark.asyncio
async def test_authenticate_user_success():
    mock_db = MagicMock()
    fake_db_user = {"loging": "test", "password": "hashed_secret"}

    mock_db.users.find_one = AsyncMock(return_value=fake_db_user)

    with patch("user_service.app.crud.verify_password", return_value=True):
        res = await crud.authenticate_user(mock_db, "test", "secret")
        assert res == fake_db_user


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password():
    mock_db = MagicMock()
    fake_db_user = {"loging": "test", "password": "hashed_secret"}
    mock_db.users.find_one = AsyncMock(return_value=fake_db_user)

    with patch("user_service.app.crud.verify_password", return_value=False):
        res = await crud.authenticate_user(mock_db, "test", "wrong")
        assert res is None


@pytest.mark.asyncio
async def test_list_users():
    mock_db = MagicMock()
    # Mock cursor iteration
    mock_cursor = AsyncMock()
    mock_cursor.__aiter__.return_value = [
        {"user_id": "1", "loging": "u1", "created_at": 1.0, "password": "p"},
        {"user_id": "2", "loging": "u2", "created_at": 2.0, "password": "p"}
    ]
    mock_db.users.find.return_value.limit.return_value = mock_cursor

    users = await crud.list_users(mock_db)
    assert len(users) == 2
    assert users[0].loging == "u1"


@pytest.mark.asyncio
async def test_get_user_not_found():
    mock_db = MagicMock()
    mock_db.users.find_one = AsyncMock(return_value=None)

    user = await crud.get_user(mock_db, "missing_id")
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    mock_db = MagicMock()
    mock_db.users.find_one = AsyncMock(return_value=None)

    res = await crud.authenticate_user(mock_db, "missing", "pass")
    assert res is None