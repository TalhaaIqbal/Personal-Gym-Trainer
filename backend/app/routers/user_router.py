from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from ..core.database import db
from ..schemas.user_schema import UserResponse, UserCreate, UserUpdate
from loguru import logger
from ..core.middleware import get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])

def get_user_collection() -> AsyncIOMotorCollection:
    return db["users"]

def get_user_service(collection: AsyncIOMotorCollection = Depends(get_user_collection)) -> UserService:
    repository = UserRepository(collection)
    return UserService(repository)


#------------------------------User routes------------------------------

@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate, service: UserService = Depends(get_user_service)):
    try:
        user = await service.create_user(user_data)
        if not user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    try:
        print(f"Getting user with ID: {user_id}")
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#------------------------------Admin only routes------------------------------

@router.get("/", response_model=list[UserResponse], dependencies=[Depends(get_current_admin)])
async def get_users(service: UserService = Depends(get_user_service)):
    try:
        return await service.get_all_users()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(get_current_admin)])
async def update_user(user_id: str, user_data: UserUpdate, service: UserService = Depends(get_user_service)):
    try:
        user = await service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", dependencies=[Depends(get_current_admin)])
async def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    try:
        deleted = await service.delete_user(user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))