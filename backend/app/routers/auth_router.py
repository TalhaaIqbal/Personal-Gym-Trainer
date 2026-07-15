from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Request
from ..core.middleware import bearer_scheme
from ..services.auth_service import AuthService
from ..repositories.user_repository import UserRepository
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from ..core.database import db
from ..schemas.user_schema import UserResponse
from ..schemas.auth_schema import LoginRequest, RegisterRequest, Token, RefreshTokenRequest
from datetime import datetime, timezone
import uuid
from ..core.security import decode_access_token, decode_refresh_token

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_user_collection() -> AsyncIOMotorCollection:
    return db["users"]

def get_auth_service(collection: AsyncIOMotorCollection = Depends(get_user_collection)) -> AuthService:
    repository = UserRepository(collection)
    return AuthService(repository)


@router.post("/login", response_model=Token)
async def login(
    user_data: LoginRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service)
):
    try:
        user = await service.authenticate_user(user_data.email, user_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user_id = str(user.get("_id"))
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        await service.enforce_session_limit(user_id)
        
        family_id = str(uuid.uuid4())
        
        access_token = service.create_access_token(user_id, ip=client_ip, user_agent=user_agent, family_id=family_id)
        refresh_token = service.create_refresh_token(user_id, ip=client_ip, user_agent=user_agent, family_id=family_id)
        
        access_payload = decode_access_token(access_token)
        refresh_payload = decode_refresh_token(refresh_token)
        if access_payload and refresh_payload:
            await db["sessions"].insert_one({
                "user_id": user_id,
                "access_jti": access_payload.get("jti"),
                "refresh_jti": refresh_payload.get("jti"),
                "family_id": family_id,
                "ip": client_ip,
                "user_agent": user_agent,
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)
            })
        
        return Token(access_token=access_token, refresh_token=refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/register", response_model=UserResponse)
async def register(user_data: RegisterRequest,
                   service: AuthService = Depends(get_auth_service)):
    try:
        user = await service.register_user(user_data.email, user_data.password, user_data.name, "client")
        if not user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        user["id"] = str(user.pop("_id"))
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    service: AuthService = Depends(get_auth_service),
):
    try:
        token = credentials.credentials
        await service.logout_user(token)
        return {"message": "Logged out successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshTokenRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service)
):
    try:
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        tokens = await service.refresh_tokens(
            token_data.refresh_token,
            access_token=token_data.access_token
        )
        if not tokens:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Create new tokens with current IP/user-agent
        from ..core.security import decode_refresh_token
        payload = decode_refresh_token(token_data.refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        new_access_token = service.create_access_token(user_id, ip=client_ip, user_agent=user_agent)
        new_refresh_token = service.create_refresh_token(user_id, ip=client_ip, user_agent=user_agent)
        
        return Token(access_token=new_access_token, refresh_token=new_refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))