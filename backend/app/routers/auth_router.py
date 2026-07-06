from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from ..core.database import db
from ..schemas.user_schema import UserResponse, UserCreate
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

def get_user_collection() -> AsyncIOMotorCollection:
    return db["users"]

def get_user_service(collection: AsyncIOMotorCollection = Depends(get_user_collection)) -> UserService:
    repository = UserRepository(collection)
    return UserService(repository)

@router.post("/login", response_model=Token)
async def login(user_data: LoginRequest, service: UserService = Depends(get_user_service)):
    try:
        user = await service.get_user_by_email(user_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Simple password check (in production, use hashed passwords)
        if user.get("password") != user_data.password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # For now, return user ID as token (implement proper JWT later)
        return Token(access_token=str(user.get("_id")))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register", response_model=UserResponse)
async def register(user_data: RegisterRequest, service: UserService = Depends(get_user_service)):
    try:
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        user = await service.create_user(user_create)
        if not user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
