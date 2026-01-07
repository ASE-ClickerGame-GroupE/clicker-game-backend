import pytest
from pydantic import ValidationError
from game_service.app.models import StartGameRequest, FinishGameRequest


def test_start_game_request_types():
    req = StartGameRequest(user_id="12345")
    assert req.user_id == "12345"

def test_finish_game_request_validates_dict():
    req = FinishGameRequest(
        session_id="sess_1",
        scores={"userA": 10, "userB": 20}
    )
    assert req.scores["userA"] == 10
    assert req.scores["userB"] == 20


    with pytest.raises(ValidationError):
        FinishGameRequest(
            session_id="sess_1",
            scores=100
        )

    with pytest.raises(ValidationError):
        FinishGameRequest(
            session_id="sess_1",
            scores=[10, 20]
        )