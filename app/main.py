from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    StartGameRequest,
    StartGameResponse,
    ClickEvent,
    ClickResponse,
    FinishGameRequest,
    FinishGameResponse,
)
from . import crud

app = FastAPI(title="Aim Clicker Game Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later: restrict to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/game/start", response_model=StartGameResponse)
async def start_game(body: StartGameRequest):
    session_id = await crud.start_game(body.user_id, body.difficulty)
    return StartGameResponse(session_id=session_id)


@app.post("/game/click", response_model=ClickResponse)
async def click(body: ClickEvent):
    session = await crud.update_click(body.session_id, body.hit, body.reaction_ms)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session_id")

    return ClickResponse(
        score=session.score,
        hits=session.hits,
        misses=session.misses,
    )


@app.post("/game/finish", response_model=FinishGameResponse)
async def finish(body: FinishGameRequest):
    session = await crud.finish_game(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session_id")

    duration_s = (session.finished_at or session.started_at) - session.started_at

    return FinishGameResponse(
        final_score=session.score,
        hits=session.hits,
        misses=session.misses,
        duration_s=duration_s,
        difficulty=session.difficulty,
        user_id=session.user_id,
    )
