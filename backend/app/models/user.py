from pydantic import BaseModel
from ..helper.object_id_validate import PyProjectID
from typing import Literal

class User(BaseModel):
    id: PyProjectID
    name: str
    email: str
    password: str
    role: Literal["client", "trainer", "admin"] = "client"