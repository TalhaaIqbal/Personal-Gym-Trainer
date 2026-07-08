from fastapi import APIRouter
from .availability_router import router as availability_router
from .user_router import router as user_router
from .auth_router import router as auth_router

router = APIRouter()

router.include_router(user_router)
router.include_router(auth_router)
router.include_router(availability_router)