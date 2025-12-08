from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base


class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None


class UserInDB(BaseModel):
    user_id: str
    username: str
    email: Optional[EmailStr] = None

Base = declarative_base()
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
