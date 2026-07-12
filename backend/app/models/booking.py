from pydantic import BaseModel, BeforeValidator
from typing import Annotated, Literal, Optional
from bson.objectid import ObjectId
from datetime import date, time

def validate_object_id(v: str) -> str:
    if ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid Object ID")

PyProjectID = Annotated[str, BeforeValidator(validate_object_id)]

class Booking(BaseModel):
    trainer_id: PyProjectID
    client_id: PyProjectID
    availability_id: PyProjectID | None = None
    booking_date: date
    start_time: time
    end_time: time
    status: Literal["pending", "confirmed", "cancelled"] = "pending"
    google_event_id: Optional[str] = None