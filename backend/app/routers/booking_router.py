from ..services.booking_service import BookingService
from ..repositories.booking_repository import BookingRepository
from ..repositories.availability_repository import AvailabilityRepository
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorCollection
from ..core.database import db
from ..schemas.booking_schema import BookingCreate, BookingStatusUpdate, BookingResponse, BookingWithTrainerResponse, BookingWithClientResponse
from loguru import logger
from ..core.middleware import get_current_admin, get_current_trainer, get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])

def get_booking_collection() -> AsyncIOMotorCollection:
    return db["bookings"]

def get_availability_collection() -> AsyncIOMotorCollection:
    return db["availability"]

def get_booking_service(
    booking_collection: AsyncIOMotorCollection = Depends(get_booking_collection),
    availability_collection: AsyncIOMotorCollection = Depends(get_availability_collection)
) -> BookingService:
    booking_repository = BookingRepository(booking_collection)
    availability_repository = AvailabilityRepository(availability_collection)
    return BookingService(booking_repository, availability_repository)


#------------------------------Client routes------------------------------

@router.get("/client", response_model=list[BookingWithTrainerResponse])
async def get_client_bookings_with_trainer_info(current_user = Depends(get_current_user),
                                                service: BookingService = Depends(get_booking_service)):
    try:
        bookings = await service.get_bookings_by_client_id(current_user["id"])
        return bookings
    except Exception as e:
        print(f"Error fetching client bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=BookingResponse)
async def create_booking(booking_data: BookingCreate, 
                         current_user = Depends(get_current_user), 
                         service: BookingService = Depends(get_booking_service)):
    try:
        booking = await service.create_booking(booking_data, current_user["id"])
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{booking_id}", response_model=BookingResponse, dependencies=[Depends(get_current_user)])
async def update_booking(booking_id: str, 
                         booking_data: BookingStatusUpdate, 
                         service: BookingService = Depends(get_booking_service)):
    try:
        booking = await service.update_booking(booking_id, booking_data)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#------------------------------Trainer routes------------------------------

@router.get("/trainer", response_model=list[BookingWithClientResponse])
async def get_trainer_bookings(status: str = Query(None), current_trainer = Depends(get_current_trainer), service: BookingService = Depends(get_booking_service)):
    try:
        return await service.get_bookings_by_trainer_id(current_trainer["id"], status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{booking_id}", dependencies=[Depends(get_current_trainer)])
async def delete_booking(booking_id: str, service: BookingService = Depends(get_booking_service)):
    try:
        deleted = await service.delete_booking(booking_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Booking not found")
        return {"message": "Booking deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#------------------------------Admin only routes------------------------------

@router.get("/", response_model=list[BookingResponse], dependencies=[Depends(get_current_admin)])
async def get_all_bookings(service: BookingService = Depends(get_booking_service)):
    try:
        return await service.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

