from pydantic import BaseModel, field_validator, model_validator
from datetime import date, time
from typing import Literal

def validate_date(date: date) -> None:
    if date < date.today():
        raise ValueError("Date cannot be in the past")

def validate_time_order(start_time: time, end_time: time) -> None:
    if start_time >= end_time:
        raise ValueError("Start time must be before end time")

def validate_time_overlap(start_time: time, end_time: time, existing_start: time, existing_end: time) -> None:
    if start_time < existing_end and end_time > existing_start:
        raise ValueError("Time slot overlaps with existing availability")

class BookingCreate(BaseModel):
    trainer_id: str
    booking_date: date
    start_time: time
    end_time: time

    @field_validator('booking_date')
    def validate_booking_date(cls, v):
        validate_date(v)
        return v

    @field_validator('start_time', 'end_time')
    def validate_time(cls, v):
        return v

    @model_validator(mode='after')
    def validate_time_order(self):
        validate_time_order(self.start_time, self.end_time)
        return self


class BookingUpdate(BaseModel):
    booking_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    status: Literal["pending", "confirmed", "cancelled"] | None = None

    @field_validator('booking_date')
    def validate_booking_date(cls, v):
        validate_date(v)
        return v

    @field_validator('start_time', 'end_time')
    def validate_time(cls, v):
        return v

    @model_validator(mode='after')
    def validate_time_order(self):
        validate_time_order(self.start_time, self.end_time)
        return self


class BookingResponse(BaseModel):
    id: str
    trainer_id: str
    client_id: str
    booking_date: date
    start_time: time
    end_time: time
    status: Literal["pending", "confirmed", "cancelled"] = "pending"

    @field_validator('booking_date')
    def validate_booking_date(cls, v):
        validate_date(v)
        return v

    @field_validator('start_time', 'end_time')
    def validate_time(cls, v):
        return v

    @model_validator(mode='after')
    def validate_time_order(self):
        validate_time_order(self.start_time, self.end_time)
        return self
