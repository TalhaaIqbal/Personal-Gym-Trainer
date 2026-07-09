from .base import BaseRepository
from ..models.booking import Booking

class BookingRepository(BaseRepository[Booking]):
    async def get_by_client_id(self, client_id: str, status: str = None):
        query = {"client_id": client_id}
        if status:
            query["status"] = status
        return await self.collection.find(query).to_list(length=None)
    
    async def get_by_trainer_id(self, trainer_id: str, status: str = None):
        query = {"trainer_id": trainer_id}
        if status:
            query["status"] = status
        return await self.collection.find(query).to_list(length=None)
    
    async def get_by_client_and_trainer(self, client_id: str, trainer_id: str):
        return await self.collection.find({"client_id": client_id, "trainer_id": trainer_id}).to_list(length=None)