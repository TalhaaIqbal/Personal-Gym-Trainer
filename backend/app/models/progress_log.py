from pydantic import BaseModel, field_validator, BeforeValidator
from typing import Annotated, Literal
from bson import ObjectId

def validate_object_id(v: str) -> str:
    if ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid Object ID")

PyProjectID = Annotated[str, BeforeValidator(validate_object_id)]

class ProgressLog(BaseModel):
    client_id: PyProjectID
    date: str
    weight_kg: float | None = None
    notes: str | None = None
    workout_completed: bool = False