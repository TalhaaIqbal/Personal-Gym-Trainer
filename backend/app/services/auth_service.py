from ..repositories.user_repository import UserRepository
from ..schemas.user_schema import UserCreate
from ..core.security import decode_access_token, hash_password, verify_password, create_access_token, create_refresh_token, decode_refresh_token
from datetime import timedelta, datetime, timezone
from ..core.database import db
from typing import Optional
import uuid


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

    async def register_user(self, email: str, password: str, name: str, role: str = "client") -> dict | None:
        existing = await self.repository.get_by_email(email)
        if existing:
            return None
        
        hashed_password = hash_password(password)
        
        user_create = UserCreate(
            email=email,
            password=hashed_password,
            name=name,
            role=role
        )
        
        user = await self.repository.create(user_create.model_dump())
        return user

    async def logout_user(self, token: str) -> None:
        payload = decode_access_token(token)
        if not payload:
            return

        jti = payload.get("jti")
        if jti:
            await db["blacklisted_tokens"].insert_one({
                "jti": jti,
                "expires_at": datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            })
        
        user_id = payload.get("sub")
        if user_id:
            await db["sessions"].delete_many({"user_id": user_id, "access_jti": jti})

    async def enforce_session_limit(self, user_id: str, max_sessions: int = 2) -> None:
        await db["sessions"].delete_many({
            "user_id": user_id,
            "expires_at": {"$lt": datetime.now(timezone.utc)}
        })
        
        active_sessions = await db["sessions"].count_documents({"user_id": user_id})
        
        if active_sessions >= max_sessions:
            oldest_session = await db["sessions"].find_one(
                {"user_id": user_id},
                sort=[("created_at", 1)]
            )
            if oldest_session:
                # Blacklist tokens
                if oldest_session.get("access_jti"):
                    await db["blacklisted_tokens"].insert_one({
                        "jti": oldest_session["access_jti"],
                        "expires_at": oldest_session.get("expires_at", datetime.now(timezone.utc) + timedelta(days=7))
                    })
                if oldest_session.get("refresh_jti"):
                    await db["blacklisted_tokens"].insert_one({
                        "jti": oldest_session["refresh_jti"],
                        "expires_at": oldest_session.get("expires_at", datetime.now(timezone.utc) + timedelta(days=7))
                    })
                # Delete session record
                await db["sessions"].delete_one({"_id": oldest_session["_id"]})

    def create_access_token(self, user_id: str, expires_delta: timedelta | None = None, ip: Optional[str] = None, user_agent: Optional[str] = None) -> str:
        return create_access_token(data={"sub": user_id}, expires_delta=expires_delta, ip=ip, user_agent=user_agent)

    def create_refresh_token(self, user_id: str, expires_delta: timedelta | None = None, ip: Optional[str] = None, user_agent: Optional[str] = None) -> str:
        return create_refresh_token(data={"sub": user_id}, expires_delta=expires_delta, ip=ip, user_agent=user_agent)

    async def refresh_tokens(self, refresh_token: str, access_token: Optional[str] = None) -> dict | None:
        payload = decode_refresh_token(refresh_token)
        if not payload:
            return None

        user_id = payload.get("sub")
        old_jti = payload.get("jti")
        if not user_id:
            return None

        user = await self.repository.get_by_id(user_id)
        if not user:
            return None

        # Blacklist old refresh token to prevent reuse
        if old_jti:
            await db["blacklisted_tokens"].insert_one({
                "jti": old_jti,
                "expires_at": datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            })

        # Blacklist old access token
        if access_token:
            access_payload = decode_access_token(access_token)
            if access_payload:
                access_jti = access_payload.get("jti")
                if access_jti:
                    await db["blacklisted_tokens"].insert_one({
                        "jti": access_jti,
                        "expires_at": datetime.fromtimestamp(access_payload["exp"], tz=timezone.utc)
                    })

        return {
            "access_token": self.create_access_token(user_id),
            "refresh_token": self.create_refresh_token(user_id)
        }
