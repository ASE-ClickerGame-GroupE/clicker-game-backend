from pydantic import BaseModel
from typing import Optional

class LeaderboardEntry(BaseModel):
    session_id: str
    user_id: str
    difficulty: str
    score: int
    hits: int
    misses: int
    duration_s: Optional[float] = None
