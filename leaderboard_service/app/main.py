# leaderboard_service/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .models import LeaderboardEntry
from .crud import get_leaderboard
from leaderboard_service.app.auth_deps import get_current_user, TokenData

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

@app.get("/leaderboard/total-score", response_model=List[LeaderboardEntry])
async def leaderboard_total_score(limit: int = 10):
    return await get_leaderboard(group_by="totalScores", limit=limit, me_only=False)

@app.get("/leaderboard/total-score/me", response_model=LeaderboardEntry)
async def leaderboard_total_score_me(current_user: TokenData = Depends(get_current_user)):
    data = await get_leaderboard(group_by="totalScores", me_only=True, current_user_id=current_user.user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        return data[0]

@app.get("/leaderboard/best-single-run", response_model=List[LeaderboardEntry])
async def leaderboard_best_single_run(limit: int = 10):
    return await get_leaderboard(group_by="bestScore", limit=limit, me_only=False) 

@app.get("/leaderboard/best-single-run/me", response_model=LeaderboardEntry)
async def leaderboard_best_single_run_me(current_user: TokenData = Depends(get_current_user)):
    data = await get_leaderboard(group_by="bestScore", me_only=True, current_user_id=current_user.user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        return data[0]
