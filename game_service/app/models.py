from pydantic import BaseModel
from typing import Optional


class StartGameRequest(BaseModel):
    user_id: str
   


class StartGameResponse(BaseModel):
    session_id: str


class ClickEvent(BaseModel):
    session_id: str
    reaction_ms: int


class ClickResponse(BaseModel):
    scores: int
  

class FinishGameRequest(BaseModel):
    session_id: str
    scores: int 
    finished_at: Optional[float] = None


class FinishGameResponse(BaseModel):
    scores: int 
    session_id: str
    finished_at: Optional[float] = None


class GameSessionInDB(BaseModel):
    session_id: str
    user_id: str
    scores: int 
    started_at: float
    finished_at: Optional[float] = None
