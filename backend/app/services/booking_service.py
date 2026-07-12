from ..repositories.booking_repository import BookingRepository
from ..repositories.availability_repository import AvailabilityRepository
from ..schemas.booking_schema import BookingCreate, BookingStatusUpdate
from .google_calendar_service import GoogleCalendarSyncService
from datetime import date, time

class BookingService:
    def __init__(self, repository: BookingRepository, availability_repository: AvailabilityRepository) -> None:
        self.repository = repository
        self.availability_repository = availability_repository
        self.calendar_sync_service = GoogleCalendarSyncService()

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
        bookings = await self.repository.get_by_trainer_id_with_client_info(trainer_id, status)
        return [self._convert_to_response(booking) for booking in bookings]

    async def create_booking(self, booking: BookingCreate, client_id: str):
        booking_dict = booking.model_dump()
        booking_dict["client_id"] = client_id
        booking_dict["status"] = "pending"

        booking_dict = self._convert_datetime_to_string(booking_dict)

        # If availability_id is not provided, try to find matching availability
        if not booking_dict.get("availability_id"):
            availability = await self.availability_repository.find_by_trainer_date_time(
                booking_dict["trainer_id"],
                booking_dict["booking_date"],
                booking_dict["start_time"],
                booking_dict["end_time"]
            )
            if availability:
                booking_dict["availability_id"] = str(availability["_id"])

        result = await self.repository.create(booking_dict)
        booking_response = self._convert_to_response(result)

        # Sync with Google Calendar if enabled
        await self.calendar_sync_service.sync_booking_to_calendar(booking_response, "create")

        return booking_response
    
    async def update_booking(self, booking_id: str, booking: BookingStatusUpdate):
        booking_dict = booking.model_dump()
        result = await self.repository.update(booking_id, booking_dict)
        booking_response = self._convert_to_response(result)

        # Sync with Google Calendar if enabled
        await self.calendar_sync_service.sync_booking_to_calendar(booking_response, "update")

        return booking_response

    async def delete_booking(self, booking_id: str):
        # Get booking before deletion to remove from calendar
        booking = await self.repository.get_by_id(booking_id)
        if booking and booking.get("google_event_id"):
            # Remove from both trainer and client calendars
            if booking.get("trainer_id"):
                await self.calendar_sync_service.remove_calendar_event(booking["google_event_id"], booking["trainer_id"])
            if booking.get("client_id"):
                await self.calendar_sync_service.remove_calendar_event(booking["google_event_id"], booking["client_id"])

        result = await self.repository.delete(booking_id)
        return result
