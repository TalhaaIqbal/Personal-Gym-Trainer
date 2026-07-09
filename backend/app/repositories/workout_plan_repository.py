from .base import BaseRepository
from ..models.workout import WorkoutPlan

class WorkoutPlanRepository(BaseRepository[WorkoutPlan]):
    async def get_by_trainer_id(self, trainer_id: str):
        return await self.collection.find({"trainer_id": trainer_id}).to_list(length=None)
    
    async def get_by_client_id(self, client_id: str):
        return await self.collection.find({"client_id": client_id}).to_list(length=None)
    
    async def get_by_trainer_and_client(self, trainer_id: str, client_id: str):
        return await self.collection.find({"trainer_id": trainer_id, "client_id": client_id}).to_list(length=None)
