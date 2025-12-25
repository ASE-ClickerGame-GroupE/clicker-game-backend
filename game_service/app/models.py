from pydantic import BaseModel
from typing import Optional


class StartGameRequest(BaseModel):
    difficulty: str


class StartGameResponse(BaseModel):
    session_id: str


class ClickEvent(BaseModel):
    session_id: str
    hit: bool
    reaction_ms: int


class ClickResponse(BaseModel):
    score: int
    hits: int
    misses: int


class FinishGameRequest(BaseModel):
    session_id: str


class FinishGameResponse(BaseModel):
    final_score: int
    hits: int
    misses: int
    duration_s: float
    difficulty: str
    user_id: str


class GameSessionInDB(BaseModel):
    session_id: str
    user_id: str
    difficulty: str
    score: int
    hits: int
    misses: int
    started_at: float
    finished_at: Optional[float] = None
