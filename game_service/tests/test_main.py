import pytest
from types import SimpleNamespace
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from game_service.app.main import app
from game_service.app.auth_deps import TokenData, get_current_user
from game_service.app.main import start_game, finish
from game_service.app.models import (
    FinishGameRequest,
    StartGameResponse,
    FinishGameResponse,
)


@pytest.mark.asyncio
async def test_start_game_calls_crud_and_returns_session_id():
    fake_session_id = "session123"

    fake_user = TokenData(user_id="user_uuid_123", loging="test_user")

    with patch(
            "game_service.app.main.crud.start_game",
            new=AsyncMock(return_value=fake_session_id),
    ) as mock_start:
        response = await start_game(current_user=fake_user)

        assert isinstance(response, StartGameResponse)
        assert response.session_id == fake_session_id

        mock_start.assert_awaited_once_with("user_uuid_123")


@pytest.mark.asyncio
async def test_finish_calls_crud_and_returns_finishresponse():
    fake_session = SimpleNamespace(
        session_id="sessionXYZ",
        scores={"user_uuid_123": 100},
        started_at=0.0,
        finished_at=20.0,
        user_id=["user_uuid_123"],
    )

    fake_user = TokenData(user_id="user_uuid_123", loging="test_user")

    with patch(
            "game_service.app.main.crud.finish_game",
            new=AsyncMock(return_value=fake_session),
    ) as mock_finish:
        body = FinishGameRequest(
            session_id="sessionXYZ",
            scores={"user_uuid_123": 100},
            finished_at=20.0,
        )

        response = await finish(body, current_user=fake_user)

        assert isinstance(response, FinishGameResponse)
        assert response.session_id == "sessionXYZ"

        mock_finish.assert_awaited_once_with(
            session_id="sessionXYZ",
            final_scores={"user_uuid_123": 100},
            finished_at=20.0
        )


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_finish_game_not_found():
    fake_user = TokenData(user_id="u1", loging="test")

    # Mock crud to return None (Session not found)
    with patch("game_service.app.main.crud.finish_game", new=AsyncMock(return_value=None)):
        # Override Auth
        app.dependency_overrides[get_current_user] = lambda: fake_user

        body = {"session_id": "missing", "scores": {}}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/game/finish", json=body)

        app.dependency_overrides = {}

    assert response.status_code == 404