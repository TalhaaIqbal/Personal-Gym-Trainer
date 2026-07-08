from ..services.availability_service import AvailabilityService
from ..repositories.availability_repository import AvailabilityRepository
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from ..core.database import db
from ..schemas.availability_schema import AvailabilityResponse, AvailabilityCreate, AvailabilityUpdate
from loguru import logger
from ..core.middleware import get_current_admin, get_current_trainer, get_current_user

router = APIRouter(prefix="/availability", tags=["Availability"])

def get_availability_collection() -> AsyncIOMotorCollection:
    return db["availability"]

def get_availability_service(collection: AsyncIOMotorCollection = Depends(get_availability_collection)) -> AvailabilityService:
    repository = AvailabilityRepository(collection)
    return AvailabilityService(repository)


#------------------------------Trainer routes------------------------------

@router.post("/", response_model=AvailabilityResponse,
                  dependencies=[Depends(get_current_trainer)])
async def create_availability(availability_data: AvailabilityCreate, 
                              service: AvailabilityService = Depends(get_availability_service)):
    try:
        availability = await service.create_availability(availability_data)
        if not availability:
            raise HTTPException(status_code=400, detail="Availability with this email already exists")
        return availability
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{trainer_id}", response_model=AvailabilityResponse, dependencies=[Depends(get_current_trainer)])
async def update_availability(trainer_id: str, availability_data: AvailabilityUpdate, service: AvailabilityService = Depends(get_availability_service)):
    try:
        availability = await service.update_availability(trainer_id, availability_data)
        if not availability:
            raise HTTPException(status_code=404, detail="Availability not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{trainer_id}", dependencies=[Depends(get_current_trainer)])
async def delete_availability(trainer_id: str, service: AvailabilityService = Depends(get_availability_service)):
    try:
        deleted = await service.delete_availability(trainer_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Availability not found")
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#------------------------------Client routes + Trainer routes------------------------------

@router.get("/{trainer_id}", response_model=list[AvailabilityResponse], dependencies=[Depends(get_current_user)])
async def get_availability(trainer_id: str, service: AvailabilityService = Depends(get_availability_service)):
    try:
        print(f"Getting availability with ID: {trainer_id}")
        availability = await service.get_availabilities_by_trainer_id(trainer_id)
        if not availability:
            raise HTTPException(status_code=404, detail="Availability not found")
        return availability
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#------------------------------Admin only routes------------------------------

@router.get("/", response_model=list[AvailabilityResponse], dependencies=[Depends(get_current_admin)])
async def get_availabilities(service: AvailabilityService = Depends(get_availability_service)):
    try:
        return await service.get_all_availabilities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

