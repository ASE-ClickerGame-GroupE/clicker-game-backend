from pydantic import BaseModel
from typing import List, Optional

class LeaderboardEntry(BaseModel):
    id: str
    userName: str
    totalGames: int
    totalScores: Optional[int] = None
    bestScore: Optional[int] = None
    place: int
