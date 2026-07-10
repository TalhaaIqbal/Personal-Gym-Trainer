from ..repositories.workout_plan_repository import WorkoutPlanRepository
from ..schemas.workout_plan_schema import WorkoutPlanCreate, WorkoutPlanUpdate
from datetime import date

class WorkoutPlanService:
    def __init__(self, repository: WorkoutPlanRepository) -> None:
        self.repository = repository

    def _convert_to_response(self, workout_doc: dict) -> dict:
        if not workout_doc:
            return None
        if "_id" in workout_doc:
            workout_doc["id"] = str(workout_doc.pop("_id"))
        return workout_doc

    def _convert_datetime_to_string(self, data: dict) -> dict:
        if "start_date" in data and isinstance(data["start_date"], date):
            data["start_date"] = data["start_date"].isoformat()
        if "end_date" in data and isinstance(data["end_date"], date):
            data["end_date"] = data["end_date"].isoformat()
        if "days" in data and isinstance(data["days"], list):
            for day in data["days"]:
                if "date" in day and isinstance(day["date"], date):
                    day["date"] = day["date"].isoformat()
        return data

    async def get_all_workout_plans(self):
        workout_plans = await self.repository.find_all()
        return [self._convert_to_response(plan) for plan in workout_plans]

    async def get_workout_plan_by_id(self, plan_id: str):
        plan = await self.repository.get_by_id(plan_id)
        return self._convert_to_response(plan)

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

    async def delete_workout_plan(self, plan_id: str):
        result = await self.repository.delete(plan_id)
        return result
