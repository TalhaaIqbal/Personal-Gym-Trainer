from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from datetime import date, time
from typing import Literal
from ..helper.date_time_validate import validate_date, validate_time_order

class BookingBase(BaseModel):
    trainer_id: str
    availability_id: str | None = None
    booking_date: date
    start_time: time
    end_time: time
    timezone: str = "UTC"
    
    @field_validator('booking_date')
    @classmethod 
    def validate_booking_date(cls, v):
        validate_date(v)
        return v

    @model_validator(mode='after')
    def validate_time_range(self):  
        validate_time_order(self.start_time, self.end_time)
        return self
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",        
        str_strip_whitespace=True 
    )


class BookingResponseBase(BaseModel):
    trainer_id: str
    availability_id: str | None = None
    booking_date: date
    start_time: time
    end_time: time
    id: str
    client_id: str
    status: Literal["pending", "confirmed", "cancelled"] = "pending"
    google_event_id: str | None = None
    
    @model_validator(mode='after')
    def validate_time_range(self):  
        validate_time_order(self.start_time, self.end_time)
        return self

class BookingCreate(BookingBase):
    pass


class BookingStatusUpdate(BaseModel):
    status: Literal["pending", "confirmed", "cancelled"]
    
    model_config = ConfigDict(extra="forbid") 


class BookingResponse(BookingResponseBase):
    pass


class TrainerInfo(BaseModel):
    name: str
    email: str
  
class ClientInfo(BaseModel):
    name: str
    email: str

class BookingWithTrainerResponse(BookingResponseBase):
    trainer_info: TrainerInfo | None = None

class BookingWithClientResponse(BookingResponseBase):
    client_info: ClientInfo | None = None