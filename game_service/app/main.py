from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from game_service.app.auth_deps import get_current_user, TokenData
import time
from typing import Optional, List

from .models import (
    StartGameResponse,
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
async def get_games(current_user: TokenData = Depends(get_current_user)):
    return await crud.list_sessions(user_id=current_user.user_id)


@app.post("/game/start", response_model=StartGameResponse)
async def start_game(current_user: TokenData = Depends(get_current_user)):
    session_id = await crud.start_game(current_user.user_id)
    return StartGameResponse(session_id=session_id)


@app.post("/game/finish", response_model=FinishGameResponse)
async def finish(body: FinishGameRequest, current_user: TokenData = Depends(get_current_user)):
    session = await crud.finish_game(
        session_id=body.session_id,
        final_scores=body.scores,
        finished_at=body.finished_at
    )

    if not session:
        raise HTTPException(status_code=404, detail="Invalid session_id")

    return FinishGameResponse(
        session_id=session.session_id
    )
