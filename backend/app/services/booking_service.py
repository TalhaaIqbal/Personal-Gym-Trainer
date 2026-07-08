from ..repositories.booking_repository import BookingRepository
from ..schemas.booking_schema import BookingCreate, BookingUpdate
from bson import ObjectId

class BookingService:
    def __init__(self, repository: BookingRepository) -> None:
        self.repository = repository

    def _convert_to_response(self, booking_doc: dict) -> dict:
        if not booking_doc:
            return None
        booking_doc["id"] = str(booking_doc.pop("_id"))
        return booking_doc

    async def get_all_bookings(self):
        bookings = await self.repository.find_all()
        return [self._convert_to_response(booking) for booking in bookings]

    async def get_booking_by_id(self, booking_id: str):
        booking = await self.repository.get_by_id(booking_id)
        return self._convert_to_response(booking)

    async def get_bookings_by_client_id(self, client_id: str):
        bookings = await self.repository.get_by_client_id(client_id)
        return [self._convert_to_response(booking) for booking in bookings]

    async def get_bookings_by_trainer_id(self, trainer_id: str):
        bookings = await self.repository.get_by_trainer_id(trainer_id)
        return [self._convert_to_response(booking) for booking in bookings]

    async def create_booking(self, booking: BookingCreate):
        booking_dict = booking.dict()
        result = await self.repository.create(booking_dict)
        return self._convert_to_response(result)
    
    async def update_booking(self, booking_id: str, booking: BookingUpdate):
        booking_dict = booking.dict(exclude_unset=True)
        result = await self.repository.update(booking_id, booking_dict)
        return self._convert_to_response(result)
    
    async def delete_booking(self, booking_id: str):
        result = await self.repository.delete(booking_id)
        return result
