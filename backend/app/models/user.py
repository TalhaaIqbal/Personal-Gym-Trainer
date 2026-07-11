from pydantic import BaseModel, BeforeValidator
from typing import Annotated, Literal
from bson.objectid import ObjectId

def validate_object_id(v: str) -> str:
    if ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid Object ID")

PyProjectID = Annotated[str, BeforeValidator(validate_object_id)]

class User(BaseModel):
    id: PyProjectID
    name: str
    email: str
    password: str
    role: Literal["client", "trainer", "admin"] = "client"