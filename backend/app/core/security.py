from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings
import uuid

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

HASHING_ALGORITHM = settings.ALGORITHM

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#-----------------Token Creation-----------------

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4()), "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=HASHING_ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4()), "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=HASHING_ALGORITHM)


#-----------------Token Decoding-----------------

def decode_token(token: str, token_type: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[HASHING_ALGORITHM])
        if payload.get("jti") is None or payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None

def decode_access_token(token: str) -> dict | None:
    return decode_token(token, "access")

def decode_refresh_token(token: str) -> dict | None:
    return decode_token(token, "refresh")