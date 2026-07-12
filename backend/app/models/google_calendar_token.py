from pydantic import BaseModel, BeforeValidator
from typing import Annotated, Optional
from bson.objectid import ObjectId

def validate_object_id(v: str) -> str:
    if ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid Object ID")

PyProjectID = Annotated[str, BeforeValidator(validate_object_id)]

class GoogleCalendarToken(BaseModel):
    user_id: PyProjectID
    google_token: str
    calendar_enabled: bool = True
