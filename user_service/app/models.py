from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None


class UserInDB(BaseModel):
    user_id: str
    username: str
    email: Optional[EmailStr] = None
