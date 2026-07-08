from ..repositories.availability_repository import AvailabilityRepository
from ..schemas.availability_schema import AvailabilityCreate, AvailabilityUpdate
from datetime import date, time

class AvailabilityService:
    def __init__(self, repository: AvailabilityRepository) -> None:
        self.repository = repository

    def _convert_to_response(self, availability_doc: dict) -> dict:
        if not availability_doc:
            return None
        availability_doc["id"] = str(availability_doc.pop("_id"))
        return availability_doc

    def _convert_datetime_to_string(self, data: dict) -> dict:
        if "booking_date" in data and isinstance(data["booking_date"], date):
            data["booking_date"] = data["booking_date"].isoformat()
        if "start_time" in data and isinstance(data["start_time"], time):
            data["start_time"] = data["start_time"].isoformat()
        if "end_time" in data and isinstance(data["end_time"], time):
            data["end_time"] = data["end_time"].isoformat()
        return data

    async def get_all_availabilities(self):
        availabilities = await self.repository.find_all()
        return [self._convert_to_response(availability) for availability in availabilities]

    async def get_availabilities_by_trainer_id(self, trainer_id: str):
        availability_list = await self.repository.get_all_availabilities_by_trainer_id(trainer_id)
        return [self._convert_to_response(availability) for availability in availability_list]

    async def create_availability(self, availability: AvailabilityCreate):
        availability_dict = availability.model_dump()
        availability_dict = self._convert_datetime_to_string(availability_dict)
        result = await self.repository.create(availability_dict)
        return self._convert_to_response(result)
    
    async def update_availability(self, trainer_id: str, availability: AvailabilityUpdate):
        availability_dict = availability.model_dump(exclude_unset=True)
        availability_dict = self._convert_datetime_to_string(availability_dict)
        result = await self.repository.update(trainer_id, availability_dict)
        return self._convert_to_response(result)
    
    async def delete_availability(self, trainer_id: str):
        result = await self.repository.delete(trainer_id)
        return result

