from .base import BaseRepository
from ..models.google_calendar_token import GoogleCalendarToken

class GoogleCalendarTokenRepository(BaseRepository[GoogleCalendarToken]):
    async def get_by_user_id(self, user_id: str):
        return await self.collection.find_one({"user_id": user_id})
