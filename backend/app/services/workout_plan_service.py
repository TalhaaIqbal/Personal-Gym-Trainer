from ..repositories.workout_plan_repository import WorkoutPlanRepository
from ..schemas.workout_plan_schema import WorkoutPlanCreate, WorkoutPlanUpdate
from .base import BaseService

class WorkoutPlanService(BaseService):
    def __init__(self, repository: WorkoutPlanRepository) -> None:
        self.repository = repository

    async def get_workout_plans_by_trainer(self, trainer_id: str):
        plans = await self.repository.get_by_trainer_id(trainer_id)
        return [self._convert_to_response(plan) for plan in plans]

    async def get_workout_plans_by_client(self, client_id: str):
        plans = await self.repository.get_by_client_id(client_id)
        return [self._convert_to_response(plan) for plan in plans]

    async def get_workout_plans_by_trainer_and_client(self, trainer_id: str, client_id: str):
        plans = await self.repository.get_by_trainer_and_client(trainer_id, client_id)
        return [self._convert_to_response(plan) for plan in plans]

    async def create_workout_plan(self, workout_plan: WorkoutPlanCreate, trainer_id: str):
        workout_dict = workout_plan.model_dump()
        workout_dict["trainer_id"] = trainer_id
        workout_dict["status"] = "active"
        workout_dict = self._convert_datetime_to_string(workout_dict)
        result = await self.repository.create(workout_dict)
        return self._convert_to_response(result)

    async def update_workout_plan(self, plan_id: str, workout_plan: WorkoutPlanUpdate):
        workout_dict = workout_plan.model_dump(exclude_unset=True)
        workout_dict = self._convert_datetime_to_string(workout_dict)
        result = await self.repository.update(plan_id, workout_dict)
        return self._convert_to_response(result)
