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

        sort_stage = next((stage for stage in pipeline if "$sort" in stage), None)
        assert sort_stage is not None
        assert "totalScores" in sort_stage["$sort"]


@pytest.mark.asyncio
async def test_get_leaderboard_best_score(mock_db):
    with patch("leaderboard_service.app.crud.get_db", return_value=mock_db):
        await crud.get_leaderboard(group_by="bestScore", limit=5)

        pipeline = mock_db.sessions.aggregate.call_args[0][0]

        sort_stage = next((stage for stage in pipeline if "$sort" in stage), None)
        assert sort_stage is not None
        assert "bestScore" in sort_stage["$sort"]


@pytest.mark.asyncio
async def test_get_leaderboard_me_only_success(mock_db):
    current_uid = "user_123"
    with patch("leaderboard_service.app.crud.get_db", return_value=mock_db):
        await crud.get_leaderboard(me_only=True, current_user_id=current_uid)

        pipeline = mock_db.sessions.aggregate.call_args[0][0]

        # Verify the pipeline contains the specific match for the user ID
        # We look for all $match stages
        match_stages = [stage for stage in pipeline if "$match" in stage]

        # There should be at least two:
        # 1. finished_at != None
        # 2. _id == current_uid
        assert len(match_stages) >= 2

        # Check the last match stage is our ID filter
        user_filter = match_stages[-1]["$match"]
        assert user_filter == {"_id": current_uid}


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