from .base import BaseRepository
from ..models.user import User

class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str):
        return await self.collection.find_one({"email": email})
    
    async def get_by_id(self, user_id: str):
        return await self.collection.find_one({"_id": user_id})

    async def get_by_role(self, role: str):
        cursor = self.collection.find({"role": role})
        return await cursor.to_list(length=None)