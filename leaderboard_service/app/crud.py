from typing import List, Optional
from .db import get_db
from .models import LeaderboardEntry
from pymongo import DESCENDING


async def get_leaderboard(
    group_by: str = "totalScores",
    me_only: bool = False,
    current_user_id: Optional[str] = None,
    limit: int = 10
) -> List[LeaderboardEntry]:
    db = get_db()

    # Determine the score calculation
    if group_by == "totalScores":
        score_field = {"totalScores": {"$sum": "$user_score"}}
    elif group_by == "bestScore":
        score_field = {"bestScore": {"$max": "$user_score"}}
    else:
        raise ValueError("Invalid group_by value")

    pipeline = [
        # 1️⃣ Only finished sessions
        {"$match": {"finished_at": {"$ne": None}}},

        # 2️⃣ Convert user_id array and scores dict into one document per user
        {"$project": {
            "user_id": 1,
            "scores": 1,
            "finished_at": 1
        }},
        {"$unwind": "$user_id"},  # create one doc per user in session
        {"$set": {"user_score": {"$getField": {"field": "$user_id", "input": "$scores"}}}},

        # 3️⃣ Group by user
        {"$group": {
            "_id": "$user_id",
            "totalGames": {"$sum": 1},
            **score_field
        }},

        # 4️⃣ Lookup username from users collection
        {"$lookup": {
            "from": "users",
            "localField": "_id",
            "foreignField": "user_id",
            "as": "user_info"
        }},
        {"$set": {"userName": {"$arrayElemAt": ["$user_info.loging", 0]}}},

        # 5️⃣ Sort by score descending
        {"$sort": {list(score_field.keys())[0]: -1}},

        # 6️⃣ Rank users
        {"$setWindowFields": {
            "sortBy": {list(score_field.keys())[0]: -1},
            "output": {"place": {"$rank": {}}}
        }},
    ]

    # 7️⃣ Apply limit for public leaderboard
    if limit and not me_only:
        pipeline.append({"$limit": limit})

    # 8️⃣ Filter for current user if me_only
    if me_only:
        if not current_user_id:
            raise ValueError("current_user_id must be provided when me_only is True")
        pipeline.append({"$match": {"_id": current_user_id}})

    # 9️⃣ Final projection
    pipeline.append({
        "$project": {
            "id": "$_id",
            "userName": 1,
            "totalGames": 1,
            group_by: 1,
            "place": 1,
            "_id": 0
        }
    })

    cursor = db.sessions.aggregate(pipeline)
    data = await cursor.to_list(length=limit if not me_only else 1)
    return data
