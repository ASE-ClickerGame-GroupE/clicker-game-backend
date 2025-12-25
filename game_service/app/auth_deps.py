from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os

# Of course this needs to be same environment variables as User Service
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
AUTH_TOKEN_URL_IN_USER_SERVICE = os.getenv("AUTH_TOKEN_URL_IN_USER_SERVICE", "http://localhost:8002/auth/token")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_TOKEN_URL_IN_USER_SERVICE)

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Stateless verification. We verify the signature and return the user_id (loging).
    We DO NOT check the database.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")