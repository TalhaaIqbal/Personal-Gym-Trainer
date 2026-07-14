from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson.objectid import ObjectId
from .security import decode_access_token
from .database import db
from datetime import datetime, timezone
from typing import Literal

bearer_scheme = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Check if token is blacklisted
    jti = payload.get("jti")
    if jti:
        blacklisted = await db["blacklisted_tokens"].find_one({"jti": jti})
        if blacklisted:
            # Clean up expired blacklisted tokens
            if blacklisted.get("expires_at") < datetime.now(timezone.utc):
                await db["blacklisted_tokens"].delete_one({"jti": jti})
            else:
                raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
    except (ValueError, TypeError):
        raise credentials_exception

    if user is None:
        raise credentials_exception

    # Convert ObjectId to string
    user["id"] = str(user.pop("_id"))
    return user


async def _require_role(current_user: dict, required_role: Literal["admin", "trainer", "client"]) -> dict:
    if current_user.get("role") != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{required_role.capitalize()}s only",
        )
    return current_user


async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    return await _require_role(current_user, "admin")


async def get_current_trainer(current_user: dict = Depends(get_current_user)) -> dict:
    return await _require_role(current_user, "trainer")


async def get_current_client(current_user: dict = Depends(get_current_user)) -> dict:
    return await _require_role(current_user, "client")