import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from leaderboard_service.app import crud


@pytest.fixture
def mock_db():
    mock = MagicMock()
    mock.sessions = MagicMock()
    mock.sessions.aggregate.return_value = AsyncMock()
    # Mock to_list execution
    mock.sessions.aggregate.return_value.to_list.return_value = []
    return mock


@pytest.mark.asyncio
async def test_get_leaderboard_total_scores(mock_db):
    with patch("leaderboard_service.app.crud.get_db", return_value=mock_db):
        await crud.get_leaderboard(group_by="totalScores", limit=5)

        mock_db.sessions.aggregate.assert_called_once()
        pipeline = mock_db.sessions.aggregate.call_args[0][0]

        assert pipeline[0]["$match"]["finished_at"]["$ne"] is None
        sort_stage = next((stage for stage in pipeline if "$sort" in stage), None)
        assert sort_stage is not None, "Sort stage not found in pipeline"
        assert "totalScores" in sort_stage["$sort"]


@pytest.mark.asyncio
async def test_get_leaderboard_invalid_group_by(mock_db):
    with patch("leaderboard_service.app.crud.get_db", return_value=mock_db):
        with pytest.raises(ValueError):
            await crud.get_leaderboard(group_by="INVALID")


@pytest.mark.asyncio
async def test_get_leaderboard_me_only_requires_id(mock_db):
    with patch("leaderboard_service.app.crud.get_db", return_value=mock_db):
        with pytest.raises(ValueError):
            await crud.get_leaderboard(me_only=True, current_user_id=None)