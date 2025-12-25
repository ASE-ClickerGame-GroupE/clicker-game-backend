import pytest
from pydantic import ValidationError
from game_service.app.models import ClickEvent, StartGameRequest

def test_click_event_validation_valid():
    event = ClickEvent(session_id="s1", hit=True, reaction_ms=100)
    assert event.reaction_ms == 100

def test_click_event_validation_missing_field():
    with pytest.raises(ValidationError):
        ClickEvent(session_id="s1", reaction_ms=100) # Missing 'hit'

def test_start_game_request_types():
    # Ensure user_id is cast to string if possible, or validated
    req = StartGameRequest(user_id="12345")
    assert req.user_id == "12345"