from pydantic import BaseModel
from datetime import date, time
from ..helper.object_id_validate import PyProjectID

class Booking(BaseModel):
    trainer_id: PyProjectID
    client_id: PyProjectID
    availability_id: PyProjectID | None = None
    booking_date: date
    start_time: time
    end_time: time
    status: Literal["pending", "confirmed", "cancelled"] = "pending"
    google_event_id: Optional[str] = None