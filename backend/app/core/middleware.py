from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from .security import decode_access_token
from .database import db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    # Convert objectId to string
    user["id"] = str(user.pop("_id"))
    return user

async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if not current_user.get("is_trainer", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user