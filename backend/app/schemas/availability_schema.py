from pydantic import BaseModel, field_validator, model_validator
from datetime import date, time

def validate_date(date: date) -> None:
    if date < date.today():
        raise ValueError("Date cannot be in the past")

def validate_time_order(start_time: time, end_time: time) -> None:
    if start_time >= end_time:
        raise ValueError("Start time must be before end time")

def validate_time_overlap(start_time: time, end_time: time, existing_start: time, existing_end: time) -> None:
    if start_time < existing_end and end_time > existing_start:
        raise ValueError("Time slot overlaps with existing availability")


class AvailabilityCreate(BaseModel):
    trainer_id: str
    booking_date: date
    start_time: time
    end_time: time

    @field_validator('booking_date')
    @classmethod
    def validate_date(cls, v: date) -> date:
        validate_date(v)
        return v

    @model_validator(mode='after')
    def validate_time_order(self) -> 'AvailabilityCreate':
        validate_time_order(self.start_time, self.end_time)
        return self


class AvailabilityUpdate(BaseModel):
    booking_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None

    @field_validator('booking_date')
    @classmethod
    def validate_date(cls, v: date) -> date:
        validate_date(v)
        return v

    @model_validator(mode='after')
    def validate_time_order(self) -> 'AvailabilityUpdate':
        if self.start_time and self.end_time:
            validate_time_order(self.start_time, self.end_time)
        return self



class AvailabilityResponse(BaseModel):
    id: str
    trainer_id: str
    booking_date: date
    start_time: time
    end_time: time

    @field_validator('booking_date')
    @classmethod
    def validate_date(cls, v: date) -> date:
        validate_date(v)
        return v

    @model_validator(mode='after')
    def validate_time_order(self) -> 'AvailabilityResponse':
        validate_time_order(self.start_time, self.end_time)
        return self