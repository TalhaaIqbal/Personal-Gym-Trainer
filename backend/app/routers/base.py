from fastapi import APIRouter
from .user_router import router as user_router
from .auth_router import router as auth_router
from .availability_router import router as availability_router
from .booking_router import router as booking_router
from .workout_plan_router import router as workout_plan_router
from .file_router import router as file_router

router = APIRouter()

router.include_router(user_router)
router.include_router(auth_router)
router.include_router(availability_router)
router.include_router(booking_router)
router.include_router(workout_plan_router)
router.include_router(file_router)