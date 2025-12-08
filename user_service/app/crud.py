import uuid
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from user_service.app.db import get_db
from user_service.app.models import UserCreate, UserInDB
from user_service.app.auth.auth import hash_password, verify_password


# Create a new user
async def create_user(db: AsyncIOMotorDatabase, data: UserCreate) -> UserInDB:
    user_id = str(uuid.uuid4())
    hashed_pwd = hash_password(data.password)

    doc = {
        "user_id": user_id,
        "loging": data.loging,      # match frontend
        "password": hashed_pwd,     # store hashed password
        "email": data.email,
    }

    await db.users.insert_one(doc)

    # Remove password before returning
    doc.pop("password")
    return UserInDB(**doc)


# Get a user by user_id
async def get_user(db: AsyncIOMotorDatabase, user_id: str) -> Optional[UserInDB]:
    doc = await db.users.find_one({"user_id": user_id})
    if not doc:
        return None
    doc.pop("_id", None)
    doc.pop("password", None)  # don't return password
    return UserInDB(**doc)


# Get a user by loging (for login)
async def get_user_by_loging(db: AsyncIOMotorDatabase, loging: str) -> Optional[dict]:
    doc = await db.users.find_one({"loging": loging})
    return doc


# Authenticate a user
async def authenticate_user(db: AsyncIOMotorDatabase, loging: str, password: str) -> Optional[dict]:
    user = await get_user_by_loging(db, loging)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user


# List users (optional)
async def list_users(db: AsyncIOMotorDatabase, limit: int = 50) -> List[UserInDB]:
    cursor = db.users.find().limit(limit)
    users: List[UserInDB] = []
    async for doc in cursor:
        doc.pop("_id", None)
        doc.pop("password", None)
        users.append(UserInDB(**doc))
    return users