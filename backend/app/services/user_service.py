from .base import BaseService
from ..repositories.user_repository import UserRepository
from ..schemas.user_schema import UserCreate, UserUpdate
from ..core.database import db
from datetime import datetime, timezone, timedelta

class UserService(BaseService):
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def get_user_by_email(self, email: str):
        return await self.repository.get_by_email(email)

    async def create_user(self, user_data: UserCreate):
        existing = await self.repository.get_by_email(user_data.email)
        if existing:
            return None

        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["password"] = (user_data.password)
        user_dict["role"] = "client"

        created_user = await self.repository.create(user_dict)
        return self._convert_to_response(created_user)

    async def update_user(self, user_id: str, user_data: UserUpdate):
        user = await self.repository.get_by_id(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])
            await self._invalidate_all_user_tokens(user_id)
        
        if "role" in update_data and update_data["role"] == "admin":
            raise ValueError("Cannot assign admin role through this endpoint")

        updated_user = await self.repository.update(user_id, update_data)
        return self._convert_to_response(updated_user)
    
    async def _invalidate_all_user_tokens(self, user_id: str) -> None:
        # Blacklist all active sessions
        sessions = await db["sessions"].find({"user_id": user_id}).to_list(length=None)
        
        for session in sessions:
            # Blacklist access token
            if session.get("access_jti"):
                await db["blacklisted_tokens"].insert_one({
                    "jti": session["access_jti"],
                    "expires_at": session.get("expires_at", datetime.now(timezone.utc) + timedelta(days=7))
                })
            # Blacklist refresh token
            if session.get("refresh_jti"):
                await db["blacklisted_tokens"].insert_one({
                    "jti": session["refresh_jti"],
                    "expires_at": session.get("expires_at", datetime.now(timezone.utc) + timedelta(days=7))
                })
        
        await db["sessions"].delete_many({"user_id": user_id})

    async def delete_user(self, user_id: str):
        return await self.repository.delete(user_id)


    #-------Trainer / Client-------#
    async def get_by_role(self, role: str):
        roled_users = await self.repository.get_by_role(role)
        print("Roled users:", roled_users)
        return [self._convert_to_response(user) for user in roled_users]