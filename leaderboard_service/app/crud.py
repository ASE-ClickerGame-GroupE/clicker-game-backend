# leaderboard_service/app/crud.py
from typing import List
from .db import get_db
from .models import LeaderboardEntry


async def get_leaderboard(limit: int = 10) -> List[LeaderboardEntry]:
    db = get_db()

    # sessions completed (finished_at not null), sorted by score desc
    cursor = (
        db.sessions.find({"finished_at": {"$ne": None}})
        .sort("score", -1)
        .limit(limit)
    )

    results: List[LeaderboardEntry] = []
    async for doc in cursor:
        doc.pop("_id", None)
        duration_s = None
        if doc.get("started_at") is not None and doc.get("finished_at") is not None:
            duration_s = doc["finished_at"] - doc["started_at"]

        results.append(
            LeaderboardEntry(
                session_id=doc["session_id"],
                user_id=doc["user_id"],
                difficulty=doc["difficulty"],
                score=doc["score"],
                hits=doc["hits"],
                misses=doc["misses"],
                duration_s=duration_s,
            )
        )

    return results
