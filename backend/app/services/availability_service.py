from ..repositories.availability_repository import AvailabilityRepository
from ..schemas.availability_schema import AvailabilityCreate, AvailabilityUpdate
from datetime import date, time
from datetime import datetime

class AvailabilityService:
    def __init__(self, repository: AvailabilityRepository, booking_repository = None) -> None:
        self.repository = repository
        self.booking_repository = booking_repository

    def _convert_to_response(self, availability_doc: dict) -> dict:
        if not availability_doc:
            return None
        if "_id" in availability_doc:
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

    async def get_available_slots_for_client(self, trainer_id: str):
        if not self.booking_repository:
            return await self.get_availabilities_by_trainer_id(trainer_id)
        
        availability_list = await self.repository.get_all_availabilities_by_trainer_id(trainer_id)
        
        # Geting all bookings for trainer (pending || confirmed)
        pending_bookings = await self.booking_repository.get_by_trainer_id(trainer_id, status="pending")
        not_available_bookings = pending_bookings
        not_available_bookings.extend(await self.booking_repository.get_by_trainer_id(trainer_id, status="confirmed"))
        
        # Unique Set of booked slots (date + time range)
        booked_slots = set()
        for booking in not_available_bookings:
            booked_slots.add(f"{booking["booking_date"]}_{booking["start_time"]}_{booking["end_time"]}")

        # Filter out availability slots (cancelled or not existing)
        available_slots = []
        for availability in availability_list:
            slot = f"{availability["booking_date"]}_{availability["start_time"]}_{availability["end_time"]}"
            if slot not in booked_slots:
                available_slots.append(availability)
        
        return [self._convert_to_response(availability) for availability in available_slots]

    async def create_availability(self, availability: AvailabilityCreate):
        # Check for overlapping slots
        existing_availabilities = await self.repository.get_all_availabilities_by_trainer_id(availability.trainer_id)
        
        for existing in existing_availabilities:
            if existing["booking_date"] == availability.booking_date.isoformat():
                # Check time overlap
                existing_start = datetime.strptime(existing["start_time"], "%H:%M:%S").time()
                existing_end = datetime.strptime(existing["end_time"], "%H:%M:%S").time()
                
                if availability.start_time < existing_end and availability.end_time > existing_start:
                    raise ValueError(f"Time slot overlaps with existing availability: {existing_start} - {existing_end}")
        
        availability_dict = availability.model_dump()
        availability_dict = self._convert_datetime_to_string(availability_dict)
        result = await self.repository.create(availability_dict)
        return self._convert_to_response(result)
    
    async def update_availability(self, availability_id: str, current_user: str, availability: AvailabilityUpdate):
        existing = await self.repository.get_by_id(availability_id)
        if not existing:
            return None 

        if existing["trainer_id"] != current_user:
            return None

        availability_dict = availability.model_dump(exclude_unset=True)
        availability_dict = self._convert_datetime_to_string(availability_dict)
        result = await self.repository.update(availability_id, availability_dict)
        return self._convert_to_response(result)
    
    async def delete_availability(self, availability_id: str):
        #Cannot delete availability if booking is already set on that timeslot
        try: 
            availability = await self.repository.get_by_id(availability_id)
            if not availability:
                return None
            
            if self.booking_repository:
                pending_bookings = await self.booking_repository.get_by_availability_id(
                    availability_id, status="pending"
                )
                confirmed_bookings = await self.booking_repository.get_by_availability_id(
                    availability_id, status="confirmed"
                )
                
                if pending_bookings or confirmed_bookings:
                    return await { "error": "Cannot delete availability with existing bookings" }
            
            result = await self.repository.delete(availability_id)
            return result
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

