from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from user_service.app.auth.routes import router as auth_router
from user_service.app.database import engine
from user_service.app.models import Base

from .models import UserCreate, UserInDB
from . import crud

app = FastAPI(title="Aim Clicker User Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include auth routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/users", response_model=UserInDB)
async def create_user(user: UserCreate):
    return await crud.create_user(user)

@app.get("/users/{user_id}", response_model=UserInDB)
async def get_user(user_id: str):
    user = await crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users", response_model=List[UserInDB])
async def list_users(limit: int = 50):
    return await crud.list_users(limit=limit)
