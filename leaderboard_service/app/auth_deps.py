from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
AUTH_TOKEN_URL_IN_USER_SERVICE = os.getenv("AUTH_TOKEN_URL_IN_USER_SERVICE", "http://localhost:8002/auth/token")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_TOKEN_URL_IN_USER_SERVICE)

class TokenData(BaseModel):
    user_id: str   # The UUID
    loging: str

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Stateless verification. We verify the signature and return the loging and uuid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        loging: str = payload.get("sub")
        uid: str = payload.get("uuid")
        if uid is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return TokenData(user_id=uid, loging=loging or "Unknown")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")