import time
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    StartGameRequest,
    StartGameResponse,
    ClickEvent,
    ClickResponse,
    FinishGameRequest,
    FinishGameResponse,
    GameSessionPublicResponse
)
from . import crud

app = FastAPI(title="Aim Clicker Game Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/game", response_model=List[GameSessionPublicResponse])
async def get_games(user_id: Optional[str] = None):
    return await crud.list_sessions(user_id=user_id)


@app.post("/game/start", response_model=StartGameResponse)
async def start_game(body: StartGameRequest):
    session_id = await crud.start_game(body.user_id)
    return StartGameResponse(session_id=session_id)


@app.post("/game/click", response_model=ClickResponse)
async def click(body: ClickEvent):
    session = await crud.update_click(body.session_id, body.reaction_ms)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session_id")

    return ClickResponse(
        scores=session.scores
       
    )


@app.post("/game/finish", response_model=FinishGameResponse)
async def finish(body: FinishGameRequest):
    session = await crud.finish_game(
        session_id=body.session_id,
        final_score=body.scores,
        finished_at=body.finished_at
    )

    if not session:
        raise HTTPException(status_code=404, detail="Invalid session_id")

    end_time = session.finished_at if session.finished_at else time.time()
    duration_s = (session.finished_at or session.started_at) - session.started_at

    return FinishGameResponse(
        session_id=session.session_id
        
    )
