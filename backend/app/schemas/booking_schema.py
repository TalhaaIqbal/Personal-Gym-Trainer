from pydantic import BaseModel
from datetime import date, time
from typing import Literal

class BookingCreate(BaseModel):
    trainer_id: str
    booking_date: date
    start_time: time
    end_time: time

class BookingUpdate(BaseModel):
    booking_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    status: Literal["pending", "confirmed", "cancelled"] | None = None

class BookingResponse(BaseModel):
    id: str
    trainer_id: str
    client_id: str
    booking_date: date
    start_time: time
    end_time: time
    status: Literal["pending", "confirmed", "cancelled"] = "pending"
