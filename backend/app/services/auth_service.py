from ..repositories.user_repository import UserRepository
from ..schemas.user_schema import UserCreate
from ..core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_refresh_token
from datetime import timedelta


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def authenticate_user(self, email: str, password: str) -> dict | None:
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.get("password")):
            return None
        
        return user

    async def register_user(self, email: str, password: str, name: str) -> dict | None:
        existing = await self.repository.get_by_email(email)
        if existing:
            return None
        
        hashed_password = hash_password(password)
        
        user_create = UserCreate(
            email=email,
            password=hashed_password,
            name=name
        )
        
        user = await self.repository.create(user_create.model_dump())
        return user

    def create_access_token(self, user_id: str, expires_delta: timedelta | None = None) -> str:
        return create_access_token(data={"sub": user_id}, expires_delta=expires_delta)

    def create_refresh_token(self, user_id: str, expires_delta: timedelta | None = None) -> str:
        return create_refresh_token(data={"sub": user_id}, expires_delta=expires_delta)

    async def refresh_tokens(self, refresh_token: str) -> dict | None:
        
        payload = decode_refresh_token(refresh_token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await self.repository.get_by_id(user_id)
        if not user:
            return None
        
        return {
            "access_token": self.create_access_token(user_id),
            "refresh_token": self.create_refresh_token(user_id)
        }
