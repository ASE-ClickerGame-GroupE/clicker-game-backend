import pytest
from unittest.mock import AsyncMock, MagicMock
from game_service.app import crud


@pytest.fixture
def mock_db():
    mock_database = MagicMock()
    mock_database.sessions = AsyncMock()
    return mock_database
