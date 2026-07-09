from ..repositories.booking_repository import BookingRepository
from ..schemas.booking_schema import BookingCreate, BookingStatusUpdate
from bson import ObjectId
from datetime import date, time

class BookingService:
    def __init__(self, repository: BookingRepository) -> None:
        self.repository = repository

    def _convert_to_response(self, booking_doc: dict) -> dict:
        if not booking_doc:
            return None
        booking_doc["id"] = str(booking_doc.pop("_id"))
        return booking_doc

    def _convert_datetime_to_string(self, data: dict) -> dict:
        if "booking_date" in data and isinstance(data["booking_date"], date):
            data["booking_date"] = data["booking_date"].isoformat()
        if "start_time" in data and isinstance(data["start_time"], time):
            data["start_time"] = data["start_time"].isoformat()
        if "end_time" in data and isinstance(data["end_time"], time):
            data["end_time"] = data["end_time"].isoformat()
        return data

    async def get_all_bookings(self):
        bookings = await self.repository.find_all()
        return [self._convert_to_response(booking) for booking in bookings]

    async def get_booking_by_id(self, booking_id: str):
        booking = await self.repository.get_by_id(booking_id)
        return self._convert_to_response(booking)

    async def get_available_bookings(self):
        bookings = await self.repository.get_available_bookings()
        return [self._convert_to_response(booking) for booking in bookings]

    async def get_bookings_by_client_id(self, client_id: str):
        bookings = await self.repository.get_by_client_id_with_trainer_info(client_id)
        return [self._convert_to_response(booking) for booking in bookings]

    async def get_bookings_by_trainer_id(self, trainer_id: str, status: str = None):
        bookings = await self.repository.get_by_trainer_id_with_client_info(trainer_id)
        return [self._convert_to_response(booking) for booking in bookings]

    async def create_booking(self, booking: BookingCreate, client_id: str):
        booking_dict = booking.model_dump()
        booking_dict["client_id"] = client_id
        booking_dict["status"] = "pending"
        booking_dict = self._convert_datetime_to_string(booking_dict)
        result = await self.repository.create(booking_dict)
        return self._convert_to_response(result)
    
    async def update_booking(self, booking_id: str, booking: BookingStatusUpdate):
        booking_dict = booking.model_dump()
        result = await self.repository.update(booking_id, booking_dict)
        return self._convert_to_response(result)
    
    async def delete_booking(self, booking_id: str):
        result = await self.repository.delete(booking_id)
        return result
