import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from game_service.app.main import start_game, finish
from game_service.app.models import (
    StartGameRequest,
    FinishGameRequest,
    StartGameResponse,
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
