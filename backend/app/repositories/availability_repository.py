from .base import BaseRepository
from ..models.availability import Availability

class AvailabilityRepository(BaseRepository[Availability]):
    async def get_all_availabilities_by_trainer_id(self, trainer_id: str):
        cursor = self.collection.find({"trainer_id": trainer_id})
        return await cursor.to_list(length=None)