import uuid
from typing import Optional, List

from .db import get_db
from .models import UserCreate, UserInDB


async def create_user(data: UserCreate) -> UserInDB:
    db = get_db()

    user_id = str(uuid.uuid4())

    doc = {
        "user_id": user_id,
        "username": data.username,
        "email": data.email,
    }

    await db.users.insert_one(doc)
    return UserInDB(**doc)


async def get_user(user_id: str) -> Optional[UserInDB]:
    db = get_db()
    doc = await db.users.find_one({"user_id": user_id})

    if not doc:
        return None

    doc.pop("_id", None)
    return UserInDB(**doc)


async def list_users(limit: int = 50) -> List[UserInDB]:
    db = get_db()
    cursor = db.users.find().limit(limit)

    users: List[UserInDB] = []
    async for doc in cursor:
        doc.pop("_id", None)
        users.append(UserInDB(**doc))

    return users
