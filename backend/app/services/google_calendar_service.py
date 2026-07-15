from ..core.google_calendar import GoogleCalendarService
from ..repositories.booking_repository import BookingRepository
from ..repositories.google_calendar_token_repository import GoogleCalendarTokenRepository
from ..repositories.user_repository import UserRepository
from ..core.database import db
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class GoogleCalendarSyncService:
    def __init__(self):
        self.user_repository = UserRepository(db["users"])
        self.calendar_token_repository = GoogleCalendarTokenRepository(db["google_calendar_tokens"])
        self.booking_repository = BookingRepository(db["bookings"])

    async def sync_booking_to_calendar(self, booking: dict, action: str):
        try:
            if not booking:
                logger.warning("Booking is None, skipping sync")
                return

            logger.info(f"Syncing booking {booking.get('id')} to calendar, action: {action}")
            logger.debug(f"Trainer ID: {booking.get('trainer_id')}, Client ID: {booking.get('client_id')}")

            # Sync for trainer if calendar enabled
            trainer_token = await self.calendar_token_repository.get_by_user_id(booking["trainer_id"])
            logger.debug(f"Trainer token found: {trainer_token is not None}")
            if trainer_token and trainer_token.get("calendar_enabled"):
                logger.info("Syncing to trainer calendar")
                await self._create_or_update_calendar_event(booking, trainer_token["google_token"], action)
            else:
                logger.debug("Trainer calendar not enabled or no token")

            # Sync for client if calendar enabled
            client_token = await self.calendar_token_repository.get_by_user_id(booking["client_id"])
            logger.debug(f"Client token found: {client_token is not None}")
            if client_token and client_token.get("calendar_enabled"):
                logger.info("Syncing to client calendar")
                await self._create_or_update_calendar_event(booking, client_token["google_token"], action)
            else:
                logger.debug("Client calendar not enabled or no token")

        except Exception as e:
            logger.error(f"Error syncing with Google Calendar: {e}", exc_info=True)

    async def _create_or_update_calendar_event(self, booking: dict, token_json: str, action: str):
        try:
            if isinstance(token_json, str):
                token_dict = json.loads(token_json)
            else:
                token_dict = token_json

            logger.debug("Token parsed successfully, creating calendar service")
            calendar_service = GoogleCalendarService()
            credentials = calendar_service.get_credentials(token_dict)
            calendar_service.build_service(credentials)
            logger.debug("Calendar service built successfully")

            # Parse booking date and time
            booking_date = booking["booking_date"]
            start_time = booking["start_time"]
            end_time = booking["end_time"]

            # Combine date and time into datetime objects
            start_datetime = datetime.combine(
                datetime.strptime(booking_date, "%Y-%m-%d").date(),
                datetime.strptime(start_time, "%H:%M:%S").time()
            )
            end_datetime = datetime.combine(
                datetime.strptime(booking_date, "%Y-%m-%d").date(),
                datetime.strptime(end_time, "%H:%M:%S").time()
            )
            
            print(start_datetime, end_datetime)

            summary = f"Training Session - Gym Booking"

            # Create or update event
            if action == "create" or not booking.get("google_event_id"):
                logger.info("Creating new calendar event")
                event_id = calendar_service.create_event(
                    summary=summary,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    description=f"Training session booking. Status: {booking['status']}"
                )
                logger.info(f"Event created with ID: {event_id}")

                await self.booking_repository.update(booking["id"], {"google_event_id": event_id})
            elif action == "update" and booking.get("google_event_id"):
                logger.info(f"Updating existing calendar event: {booking.get('google_event_id')}")
                try:
                    calendar_service.update_event(
                        event_id=booking["google_event_id"],
                        summary=summary,
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        description=f"Training session booking. Status: {booking['status']}"
                    )
                    logger.info("Event updated successfully")
                except Exception as update_error:
                    logger.warning(f"Error updating event (event might not exist): {update_error}")
                    
                    # If update fails, create new one
                    logger.info("Creating new event instead")
                    event_id = calendar_service.create_event(
                        summary=summary,
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        description=f"Training session booking. Status: {booking['status']}"
                    )
                    logger.info(f"Event created with ID: {event_id}")
                    # Save new event ID to booking
                    await self.booking_repository.update(booking["id"], {"google_event_id": event_id})

        except Exception as e:
            logger.error(f"Error creating/updating calendar event: {e}", exc_info=True)

    async def remove_calendar_event(self, event_id: str, user_id: str):
        try:
            token = await self.calendar_token_repository.get_by_user_id(user_id)
            if token and token.get("calendar_enabled"):
                calendar_service = GoogleCalendarService()
                credentials = calendar_service.get_credentials(token["google_token"])
                calendar_service.build_service(credentials)
                calendar_service.delete_event(event_id)
        except Exception as e:
            logger.error(f"Error removing calendar event: {e}", exc_info=True)
