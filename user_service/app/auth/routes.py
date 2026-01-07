from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from jose import jwt, JWTError

from user_service.app.models import UserCreate, UserInDB, Token
from user_service.app.crud import create_user, authenticate_user
from user_service.app.db import get_db
from user_service.app.auth.auth import create_access_token
from user_service.app.auth.auth import SECRET_KEY, ALGORITHM

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Signup endpoint

@router.post("/signup", response_model=UserInDB)
async def signup(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    # Check if user already exists
    existing_user = await db.users.find_one({"loging": user.loging})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    # Create user
    new_user = await create_user(db, user)
    return new_user

# Login endpoint (returns JWT token)

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    OAuth2PasswordRequestForm provides:
    - username: loging field from frontend
    - password
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token
    access_token = create_access_token(data={"sub": user["loging"], "uuid": user["user_id"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Example protected endpoint

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        loging: str = payload.get("sub")
        if loging is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.users.find_one({"loging": loging})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.pop("_id", None)
    user.pop("password", None)
    return user


@router.get("/me", response_model=UserInDB)
async def read_me(current_user: dict = Depends(get_current_user)):
    """
    Returns the currently logged-in user
    """
    return current_user