from pydantic import BaseModel
from typing import Optional, List, Dict


class GameSessionPublicResponse(BaseModel):
    id: str
    user_id: List[str]
    scores: Dict[str, int]
    started_at: float
    finished_at: Optional[float] = None

class StartGameRequest(BaseModel):
    user_id: str
   


class StartGameResponse(BaseModel):
    session_id: str


class FinishGameRequest(BaseModel):
    session_id: str
    scores: Dict[str, int]
    finished_at: Optional[float] = None


class FinishGameResponse(BaseModel):
    session_id: str



class GameSessionInDB(BaseModel):
    session_id: str
    user_id: List[str]
    scores: Dict[str, int]
    started_at: float
    finished_at: Optional[float] = None
