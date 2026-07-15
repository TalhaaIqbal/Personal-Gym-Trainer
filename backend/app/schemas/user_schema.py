from pydantic import BaseModel, EmailStr, ConfigDict, BeforeValidator
from typing import Literal, Annotated
from ..helper.password_validate import validate_password_strength

ValidPassword = Annotated[str, BeforeValidator(validate_password_strength)]
OptionalValidPassword = Annotated[ str | None, 
    BeforeValidator(lambda v: validate_password_strength(v) if v is not None else None)
]

class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: ValidPassword


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    role: Literal["client", "trainer", "admin"] | None = None
    password: OptionalValidPassword = None
    

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: Literal["client", "trainer", "admin"]

    model_config = ConfigDict(from_attributes=True)
