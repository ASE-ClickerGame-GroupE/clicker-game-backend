import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from game_service.app.main import start_game, click, finish
from game_service.app.models import StartGameRequest, ClickEvent, FinishGameRequest, StartGameResponse, ClickResponse, FinishGameResponse


@pytest.mark.asyncio
async def test_start_game_calls_crud_and_returns_session_id():
    fake_session_id = "session123"
    with patch("game_service.app.main.crud.start_game", new=AsyncMock(return_value=fake_session_id)) as mock_start:
        body = StartGameRequest(user_id="user123", difficulty="easy")
        response = await start_game(body)
        assert isinstance(response, StartGameResponse)
        assert response.session_id == fake_session_id
        mock_start.assert_awaited_once_with("user123", "easy")


@pytest.mark.asyncio
async def test_click_calls_crud_and_returns_clickresponse():
    fake_session = SimpleNamespace(score=42, hits=3, misses=1)
    with patch("game_service.app.main.crud.update_click", new=AsyncMock(return_value=fake_session)) as mock_update:
        body = ClickEvent(session_id="s1", hit=True, reaction_ms=150)
        response = await click(body)
        assert isinstance(response, ClickResponse)
        assert response.score == 42
        assert response.hits == 3
        assert response.misses == 1
        mock_update.assert_awaited_once_with("s1", True, 150)


@pytest.mark.asyncio
async def test_click_raises_404_on_invalid_session():
    with patch("game_service.app.main.crud.update_click", new=AsyncMock(return_value=None)):
        body = ClickEvent(session_id="unknown", hit=True, reaction_ms=200)
        with pytest.raises(HTTPException) as exc:
            await click(body)
        assert exc.value.status_code == 404
        assert exc.value.detail == "Invalid session_id"


@pytest.mark.asyncio
async def test_finish_calls_crud_and_returns_finishresponse():
    fake_session = SimpleNamespace(
        score=100,
        hits=10,
        misses=2,
        started_at=0.0,
        finished_at=20.0,
        difficulty="hard",
        user_id="user123",
    )
    with patch("game_service.app.main.crud.finish_game", new=AsyncMock(return_value=fake_session)) as mock_finish:
        body = FinishGameRequest(session_id="sessionXYZ")
        response = await finish(body)
        assert isinstance(response, FinishGameResponse)
        assert response.final_score == 100
        assert response.hits == 10
        assert response.misses == 2
        assert response.difficulty == "hard"
        assert response.user_id == "user123"
        assert pytest.approx(response.duration_s, rel=1e-3) == 20.0
        mock_finish.assert_awaited_once_with("sessionXYZ")
