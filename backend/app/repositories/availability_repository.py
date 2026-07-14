from .base import BaseRepository
from ..models.availability import Availability
from datetime import datetime

class AvailabilityRepository(BaseRepository[Availability]):
    async def get_all_availabilities_by_trainer_id(self, trainer_id: str):
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        cursor = self.collection.find({
            "trainer_id": trainer_id,
            "booking_date": {"$gte": today_str}
        })
        return await cursor.to_list(length=None)
    
    async def find_by_trainer_date_time(self, trainer_id: str, booking_date: str, start_time: str, end_time: str):
        return await self.collection.find_one({
            "trainer_id": trainer_id,
            "booking_date": booking_date,
            "start_time": start_time,
            "end_time": end_time
        })