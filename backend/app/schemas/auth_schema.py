from pydantic import BaseModel, EmailStr, BeforeValidator
from typing import Annotated
from ..helper.password_validate import validate_password_strength

StrongPassword = Annotated[str, BeforeValidator(validate_password_strength)]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str 

class RegisterRequest(BaseModel):
    email: EmailStr
    password: StrongPassword
    name: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    access_token: str