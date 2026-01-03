import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from game_service.app import crud


@pytest.fixture
def mock_db():
    # Setup a mock database structure: db.sessions
    mock_database = MagicMock()
    mock_database.sessions = AsyncMock()
    return mock_database


@pytest.mark.asyncio
async def test_crud_start_game_wraps_id_in_list(mock_db):
    """
    Ensures that when we pass a single string ID,
    it is saved as a List and Dict in MongoDB.
    """
    with patch("game_service.app.crud.get_db", return_value=mock_db):
        session_id = await crud.start_game("uuid-123")

        assert isinstance(session_id, str)

        mock_db.sessions.insert_one.assert_called_once()
        inserted_doc = mock_db.sessions.insert_one.call_args[0][0]

        assert inserted_doc["user_id"] == ["uuid-123"]  # Should be a List
        assert inserted_doc["scores"] == {"uuid-123": 0}  # Should be a Dict


@pytest.mark.asyncio
async def test_crud_finish_game_updates_all(mock_db):
    fake_doc = {
        "session_id": "sess_abc",
        "user_id": ["u1", "u2"],
        "scores": {"u1": 10, "u2": 20},
        "started_at": 100.0,
        "finished_at": 200.0
    }

    mock_db.sessions.update_one.return_value = AsyncMock()
    mock_db.sessions.find_one.return_value = fake_doc

    with patch("game_service.app.crud.get_db", return_value=mock_db):
        final_scores = {"u1": 10, "u2": 20}

        result = await crud.finish_game("sess_abc", final_scores, finished_at=200.0)

        mock_db.sessions.update_one.assert_called_once()
        call_args = mock_db.sessions.update_one.call_args

        update_op = call_args[0][1]

        assert update_op["$set"]["scores"] == final_scores
        assert update_op["$set"]["user_id"] == ["u1", "u2"]
        assert result.session_id == "sess_abc"