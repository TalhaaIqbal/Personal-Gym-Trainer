from ..services.availability_service import AvailabilityService
from ..repositories.availability_repository import AvailabilityRepository
from ..repositories.booking_repository import BookingRepository
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from ..core.database import db
from ..schemas.availability_schema import AvailabilityResponse, AvailabilityCreate, AvailabilityUpdate
from loguru import logger
from ..core.middleware import get_current_admin, get_current_trainer, get_current_user

router = APIRouter(prefix="/availability", tags=["Availability"])

def get_availability_collection() -> AsyncIOMotorCollection:
    return db["availability"]

def get_booking_collection() -> AsyncIOMotorCollection:
    return db["bookings"]

def get_availability_service(
    availability_collection: AsyncIOMotorCollection = Depends(get_availability_collection),
    booking_collection: AsyncIOMotorCollection = Depends(get_booking_collection)
) -> AvailabilityService:
    availability_repository = AvailabilityRepository(availability_collection)
    booking_repository = BookingRepository(booking_collection)
    return AvailabilityService(availability_repository, booking_repository)


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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{availability_id}", response_model=AvailabilityResponse)
async def update_availability(
    availability_id: str,
    availability_data: AvailabilityUpdate,
    current_user: dict = Depends(get_current_trainer),
    service: AvailabilityService = Depends(get_availability_service),
):
    try:
        availability = await service.update_availability(availability_id, str(current_user["_id"]), availability_data)
        if not availability:
            raise HTTPException(status_code=404, detail="Availability not found")
        return availability
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{availability_id}", dependencies=[Depends(get_current_trainer)])
async def delete_availability(availability_id: str, service: AvailabilityService = Depends(get_availability_service)):
    try:
        deleted = await service.delete_availability(availability_id)
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

@router.get("/{trainer_id}/available", response_model=list[AvailabilityResponse], dependencies=[Depends(get_current_user)])
async def get_available_slots(trainer_id: str, service: AvailabilityService = Depends(get_availability_service)):
    try:
        availability = await service.get_available_slots_for_client(trainer_id)
        if not availability:
            return []
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

