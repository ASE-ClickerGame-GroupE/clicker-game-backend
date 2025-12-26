from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from user_service.app.auth.routes import router as auth_router
from user_service.app.models import UserCreate, UserInDB
from user_service.app.db import get_db
from user_service.app import crud

app = FastAPI(title="Aim Clicker User Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}


# Create user (direct DB access without auth route)
@app.post("/users", response_model=UserInDB)
async def create_user_endpoint(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    return await crud.create_user(db, user)


# Get user by ID
@app.get("/users/{user_id}", response_model=UserInDB)
async def get_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# List users
@app.get("/users", response_model=List[UserInDB])
async def list_users(limit: int = 50, db: AsyncIOMotorDatabase = Depends(get_db)):
    return await crud.list_users(db, limit=limit)