import time
import uuid
from typing import Optional, List, Dict

from .db import get_db
from .models import GameSessionInDB, GameSessionPublicResponse


async def list_sessions(user_id: Optional[str] = None, limit: int = 50) -> List[dict]:
    db = get_db()

    filter_query = {}
    if user_id:
        filter_query["user_id"] = user_id

    cursor = db.sessions.find(filter_query).sort("finished_at", -1).limit(limit)

    results = []
    async for doc in cursor:
        session_data = {
            "id": doc["session_id"],
            "user_id": doc["user_id"],
            "scores": doc["scores"],
            "started_at": doc["started_at"],
            "finished_at": doc.get("finished_at")
        }
        results.append(GameSessionPublicResponse(**session_data))
    return results

async def start_game(user_id: str) -> str:
    """
    Create a new game session document in MongoDB.
    """
    db = get_db()
    session_id = str(uuid.uuid4())

    doc = {
        "session_id": session_id,
        "user_id": [user_id],
        "scores": {user_id: 0},
        "started_at": time.time(),
        "finished_at": None,
    }

    await db.sessions.insert_one(doc)
    return session_id


async def get_session(session_id: str) -> Optional[GameSessionInDB]:
    db = get_db()
    doc = await db.sessions.find_one({"session_id": session_id})
    if not doc:
        return None

    doc.pop("_id", None)
    return GameSessionInDB(**doc)


async def finish_game(
        session_id: str,
        final_scores: Dict[str, int] = None,
        finished_at: Optional[float] = None,
        ) -> Optional[GameSessionInDB]:
    """
    Mark game as finished and set finished_at timestamp.
    """
    db = get_db()

    if finished_at is None:
        finished_at = time.time()

    all_users = list(final_scores.keys())

    await db.sessions.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "scores": final_scores,
                "user_id": all_users,
                "finished_at": finished_at
            }
        },
    )

    return await get_session(session_id)
