import pytest
from pydantic import ValidationError
from game_service.app.models import StartGameRequest


def test_start_game_request_types():
    # Ensure user_id is cast to string if possible, or validated
    req = StartGameRequest(user_id="12345")
    assert req.user_id == "12345"