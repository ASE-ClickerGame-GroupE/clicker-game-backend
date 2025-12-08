import time
import uuid
from typing import Optional

from .db import get_db
from .models import GameSessionInDB


async def start_game(user_id: str) -> str:
    """
    Create a new game session document in MongoDB.
    """
    db = get_db()
    session_id = str(uuid.uuid4())

    doc = {
        "session_id": session_id,
        "user_id": user_id, 
        "scores": 0,
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

    # remove Mongo internal _id
    doc.pop("_id", None)
    return GameSessionInDB(**doc)


async def update_click(
    session_id: str,
    hit: bool,
    reaction_ms: int,
) -> Optional[GameSessionInDB]:
    """
    Update score/hits/misses for a click event.
    """
    db = get_db()
    session = await get_session(session_id)
    if not session:
        return None

    score = session.scores
  

    if hit:
        hits += 1
        score += max(1, 50 - reaction_ms // 20)
    else:
        misses += 1
        score -= 2

    await db.sessions.update_one(
        {"session_id": session_id},
        {"$set": {"scores": score}},
    )

    return await get_session(session_id)


async def finish_game(session_id: str) -> Optional[GameSessionInDB]:
    """
    Mark game as finished and set finished_at timestamp.
    """
    db = get_db()
    session = await get_session(session_id)
    if not session:
        return None

    finished_at = time.time()

    await db.sessions.update_one(
        {"session_id": session_id},
        {"$set": {"finished_at": finished_at}},
    )

    return await get_session(session_id)
