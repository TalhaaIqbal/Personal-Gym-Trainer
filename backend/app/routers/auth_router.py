from ..services.auth_service import AuthService
from ..repositories.user_repository import UserRepository
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from ..core.database import db
from ..schemas.user_schema import UserResponse
from ..schemas.auth_schema import LoginRequest, RegisterRequest, Token, RefreshTokenRequest

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_user_collection() -> AsyncIOMotorCollection:
    return db["users"]

def get_auth_service(collection: AsyncIOMotorCollection = Depends(get_user_collection)) -> AuthService:
    repository = UserRepository(collection)
    return AuthService(repository)

@router.post("/login", response_model=Token)
async def login(user_data: LoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        user = await service.authenticate_user(user_data.email, user_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user_id = str(user.get("_id"))
        access_token = service.create_access_token(user_id)
        refresh_token = service.create_refresh_token(user_id)
        
        return Token(access_token=access_token, refresh_token=refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register", response_model=UserResponse)
async def register(user_data: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    try:
        user = await service.register_user(user_data.email, user_data.password, user_data.name)
        if not user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        user["id"] = str(user.pop("_id"))
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: RefreshTokenRequest, service: AuthService = Depends(get_auth_service)):
    try:
        tokens = await service.refresh_tokens(token_data.refresh_token)
        if not tokens:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        return Token(access_token=tokens["access_token"], refresh_token=tokens["refresh_token"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))