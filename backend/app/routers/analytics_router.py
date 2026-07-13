from ..services.analytics_service import AnalyticsService
from fastapi import APIRouter, Depends, HTTPException
from ..core.middleware import get_current_trainer

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_analytics_service():
    return AnalyticsService()

@router.get("/overview")
async def get_trainer_overview(
    current_user = Depends(get_current_trainer),
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        overview = await service.get_trainer_overview(current_user["id"])
        return overview
    except Exception as e:
        print(f"Error getting trainer overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/booking-trends")
async def get_booking_trends(
    days: int = 30,
    current_user = Depends(get_current_trainer),
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        trends = await service.get_booking_trends(current_user["id"], days)
        return trends
    except Exception as e:
        print(f"Error getting booking trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/client-stats")
async def get_client_stats(
    current_user = Depends(get_current_trainer),
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        stats = await service.get_client_stats(current_user["id"])
        return stats
    except Exception as e:
        print(f"Error getting client stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/time-slots")
async def get_time_slot_analysis(
    current_user = Depends(get_current_trainer),
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        analysis = await service.get_time_slot_analysis(current_user["id"])
        return analysis
    except Exception as e:
        print(f"Error getting time slot analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/revenue")
async def get_monthly_revenue(
    months: int = 6,
    current_user = Depends(get_current_trainer),
    service: AnalyticsService = Depends(get_analytics_service)
):
    try:
        revenue = await service.get_monthly_revenue(current_user["id"], months)
        return revenue
    except Exception as e:
        print(f"Error getting monthly revenue: {e}")
        raise HTTPException(status_code=500, detail=str(e))
