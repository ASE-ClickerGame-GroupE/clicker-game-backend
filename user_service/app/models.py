from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Input schema for creating a user
class UserCreate(BaseModel):
    loging: str
    password: str
    email: Optional[EmailStr] = None

# Schema representing a user stored in DB
class UserInDB(BaseModel):
    user_id: str
    loging: str
    email: Optional[EmailStr] = None
    created_at: float


# Schema for login response token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"