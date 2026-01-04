from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
AUTH_TOKEN_URL_IN_USER_SERVICE = os.getenv("AUTH_TOKEN_URL_IN_USER_SERVICE", "http://localhost:8002/auth/token")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_TOKEN_URL_IN_USER_SERVICE)

class TokenData(BaseModel):
    user_id: str
    loging: str

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        if not SECRET_KEY or not ALGORITHM:
            raise HTTPException(status_code=500, detail="Missing SECRET_KEY/ALGORITHM in environment")
        print("GS SECRET_KEY:", SECRET_KEY)
        print("GS ALGORITHM:",ALGORITHM)
        print("GS TOKEN HEAD:", token[:20], "LEN:", len(token))
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        loging: str = payload.get("sub")
        uid: str = payload.get("uuid")
        if not uid:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return TokenData(user_id=uid, loging=loging or "Unknown")
    except JWTError:
        print("GS JWTError:", repr(e))
        raise HTTPException(status_code=401, detail="Could not validate credentials")

async def get_current_user_uuid(token: str = Depends(oauth2_scheme)) -> str:
    try:
        if not SECRET_KEY or not ALGORITHM:
            raise HTTPException(status_code=500, detail="Missing SECRET_KEY/ALGORITHM in environment")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("uuid")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
