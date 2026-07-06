from .base import BaseRepository
from ..models.user import User

class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str):
        return await self.collection.find_one({"email": email})