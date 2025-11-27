# leaderboard_service/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import LeaderboardEntry
from . import crud

app = FastAPI(title="Aim Clicker Leaderboard Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust if you have a frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 10):
    """
    Returns the top N finished game sessions ordered by score (desc).
    """
    return await crud.get_leaderboard(limit=limit)
