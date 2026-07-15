from pydantic import BaseModel, field_validator, model_validator
from datetime import date, time
from typing import Self
from ..helper.date_time_validate import validate_date, validate_time_order

class AvailabilityBase(BaseModel):
    trainer_id: str
    booking_date: date
    start_time: time
    end_time: time
    
    @field_validator('booking_date')
    @classmethod
    def check_booking_date(cls, v: date) -> date:
        validate_date(v)
        return v

    @model_validator(mode='after')
    def check_time_order(self) -> Self:
        validate_time_order(self.start_time, self.end_time)
        return self


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityUpdate(BaseModel):
    booking_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None

    @field_validator('booking_date')
    @classmethod
    def check_booking_date(cls, v: date | None) -> date | None:
        if v is not None:
            validate_date(v)
        return v

    @model_validator(mode='after')
    def check_time_order(self) -> Self:
        if self.start_time is not None and self.end_time is not None:
            validate_time_order(self.start_time, self.end_time)
        return self


class AvailabilityResponse(AvailabilityBase): 
    id: str