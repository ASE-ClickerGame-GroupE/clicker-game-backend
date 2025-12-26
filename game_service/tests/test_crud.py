import pytest
from unittest.mock import AsyncMock, MagicMock
from game_service.app import crud


@pytest.fixture
def mock_db():
    mock_database = MagicMock()
    mock_database.sessions = AsyncMock()
    return mock_database


@pytest.mark.asyncio
async def test_update_click_hit_increases_score(mock_db):
    with pytest.MonkeyPatch.context() as m:
        m.setattr("game_service.app.crud.get_db", lambda: mock_db)

        fake_session_data = {
            "session_id": "s1",
            "scores": 0,
            "user_id": "u1",
            "started_at": 100.0,
            "finished_at": None
        }
        mock_db.sessions.find_one.return_value = fake_session_data

        # ACTION: hit=True
        await crud.update_click(session_id="s1", hit=True, reaction_ms=100)

        # ASSERT
        call_args = mock_db.sessions.update_one.await_args
        update_doc = call_args[0][1]

        # 0 + (50 - 100//20) = 45
        assert update_doc["$set"]["scores"] == 45