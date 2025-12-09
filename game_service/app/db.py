import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

print("DEBUG: MONGODB_URI =", os.getenv("MONGODB_URI"))
print("DEBUG: MONGODB_DB =", os.getenv("MONGODB_DB"))

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "aim_clicker")

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGODB_URI)
    return _client


def get_db():
    return get_client()[MONGODB_DB]
