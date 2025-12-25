import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from game_service.app.main import start_game, click, finish
from game_service.app.models import (
    StartGameRequest,
    ClickEvent,
    FinishGameRequest,
    StartGameResponse,
    ClickResponse,
    FinishGameResponse,
)


@pytest.mark.asyncio
async def test_start_game_calls_crud_and_returns_session_id():
    fake_session_id = "session123"

    with patch(
            "game_service.app.main.crud.start_game",
            new=AsyncMock(return_value=fake_session_id),
    ) as mock_start:

        # In main.py, start_game takes `user_id` from dependency.
        # To unit test the endpoint function directly, we pass user_id as an argument if it's a dependency.
        response = await start_game(user_id="user123")

        assert isinstance(response, StartGameResponse)
        assert response.session_id == fake_session_id

        mock_start.assert_awaited_once_with("user123")


@pytest.mark.asyncio
async def test_click_calls_crud_and_returns_clickresponse():
    fake_session = SimpleNamespace(sessions_id="s1", scores=42)

    with patch(
            "game_service.app.main.crud.update_click",
            new=AsyncMock(return_value=fake_session),
    ) as mock_update:
        body = ClickEvent(session_id="s1", reaction_ms=150, hit=True)

        response = await click(body)

        assert isinstance(response, ClickResponse)
        assert response.scores == 42

        mock_update.assert_awaited_once_with("s1", True, 150)


@pytest.mark.asyncio
async def test_click_raises_404_on_invalid_session():
    with patch(
        "game_service.app.main.crud.update_click",
        new=AsyncMock(return_value=None),
    ):
        body = ClickEvent(session_id="unknown", reaction_ms=200, hit=True)

        with pytest.raises(HTTPException) as exc:
            await click(body)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Invalid session_id"


@pytest.mark.asyncio
async def test_finish_calls_crud_and_returns_finishresponse():
   
    fake_session = SimpleNamespace(
        session_id="sessionXYZ",
        scores=100,
        started_at=0.0,
        finished_at=20.0,
        user_id="user123",
    )

    with patch(
        "game_service.app.main.crud.finish_game",
        new=AsyncMock(return_value=fake_session),
    ) as mock_finish:
  
        body = FinishGameRequest(
            session_id="sessionXYZ",
            scores=100,
            finished_at=20.0,
        )

        response = await finish(body)

        assert isinstance(response, FinishGameResponse)
      
      
        assert response.session_id == "sessionXYZ"

        mock_finish.assert_awaited_once_with(session_id="sessionXYZ",
                                             final_score=100,
                                             finished_at=20.0)
