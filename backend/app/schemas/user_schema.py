from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

def _validate_password_strength(v: str) -> str:
    if len(v) < 8:
        raise ValueError('Password must be at least 8 characters long')
    
    has_upper = any(c.isupper() for c in v)
    has_lower = any(c.islower() for c in v)
    has_digit = any(c.isdigit() for c in v)
    has_special = any(c in "!@#$%^&*(),.?\":{}|<>" for c in v)

    if not has_upper:
        raise ValueError('Password must contain at least one uppercase letter')
    if not has_lower:
        raise ValueError('Password must contain at least one lowercase letter')
    if not has_digit:
        raise ValueError('Password must contain at least one digit')
    if not has_special:
        raise ValueError('Password must contain at least one special character')        
    return v


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    name: str | None = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validate_password_strength(v)


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    is_trainer: bool = False

    model_config = ConfigDict(from_attributes=True)