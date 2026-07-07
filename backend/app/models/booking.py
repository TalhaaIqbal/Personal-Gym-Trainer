from pydantic import BaseModel, BeforeValidator
from typing import Annotated, Literal
from bson import ObjectId

def validate_object_id(v: str) -> str:
    if ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid Object ID")

PyProjectID = Annotated[str, BeforeValidator(validate_object_id)]

class Booking(BaseModel):
    trainer_id: PyProjectID
    client_id: PyProjectID
    date: str
    start_time: str
    end_time: str
    status: Literal["pending", "confirmed", "cancelled"] = "pending"