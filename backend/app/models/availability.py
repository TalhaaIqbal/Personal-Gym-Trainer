from pydantic import BaseModel, BeforeValidator
from typing import Annotated
from bson.objectid import ObjectId
from datetime import date, time

def validate_object_id(v: str) -> str:
    if ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid Object ID")

PyProjectID = Annotated[str, BeforeValidator(validate_object_id)]

class Availability(BaseModel):
    id: PyProjectID
    trainer_id: PyProjectID
    booking_date: date
    start_time: time
    end_time: time