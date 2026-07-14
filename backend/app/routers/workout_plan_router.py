from ..services.workout_plan_service import WorkoutPlanService
from ..repositories.workout_plan_repository import WorkoutPlanRepository
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from ..core.database import db
from ..schemas.workout_plan_schema import WorkoutPlanCreate, WorkoutPlanUpdate, WorkoutPlanResponse
from loguru import logger
from ..core.middleware import get_current_admin, get_current_trainer, get_current_user
from typing import Optional

router = APIRouter(prefix="/workout-plans", tags=["Workout Plans"])

def get_workout_plan_collection() -> AsyncIOMotorCollection:
    return db["workout_plans"]

def get_workout_plan_service(collection: AsyncIOMotorCollection = Depends(get_workout_plan_collection)) -> WorkoutPlanService:
    repository = WorkoutPlanRepository(collection)
    return WorkoutPlanService(repository)


#------------------------------Trainer routes------------------------------

@router.post("/", response_model=WorkoutPlanResponse, dependencies=[Depends(get_current_trainer)])
async def create_workout_plan(workout_plan: WorkoutPlanCreate, 
                              current_trainer = Depends(get_current_trainer),
                              service: WorkoutPlanService = Depends(get_workout_plan_service)):
    try:
        plan = await service.create_workout_plan(workout_plan, current_trainer["id"])
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trainer", response_model=list[WorkoutPlanResponse], dependencies=[Depends(get_current_trainer)])
async def get_trainer_workout_plans(summary = "Get trainers workout plans that he made himself for his clients",current_trainer = Depends(get_current_trainer),
                                     service: WorkoutPlanService = Depends(get_workout_plan_service)):
    try:
        plans = await service.get_workout_plans_by_trainer(current_trainer["id"])
        return plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trainer/{client_id}", response_model=list[WorkoutPlanResponse], dependencies=[Depends(get_current_trainer)])
async def get_trainer_workout_plans_for_client(client_id: str,
                                                current_trainer = Depends(get_current_trainer),
                                                service: WorkoutPlanService = Depends(get_workout_plan_service)):
    try:
        plans = await service.get_workout_plans_by_trainer_and_client(current_trainer["id"], client_id)
        return plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{plan_id}", response_model=WorkoutPlanResponse, dependencies=[Depends(get_current_trainer)])
async def update_workout_plan(plan_id: str, 
                              workout_plan: WorkoutPlanUpdate,
                              service: WorkoutPlanService = Depends(get_workout_plan_service)):
    try:
        plan = await service.update_workout_plan(plan_id, workout_plan)
        if not plan:
            raise HTTPException(status_code=404, detail="Workout plan not found")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{plan_id}", dependencies=[Depends(get_current_trainer)])
async def delete_workout_plan(plan_id: str, service: WorkoutPlanService = Depends(get_workout_plan_service)):
    try:
        deleted = await service.delete(plan_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Workout plan not found")
        return {"message": "Workout plan deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#------------------------------Client routes------------------------------

@router.get("/client", response_model=list[WorkoutPlanResponse], dependencies=[Depends(get_current_user)])
async def get_client_workout_plans(summary = "Get Clients own workout plans", 
                                   trainer_id: Optional[str] = None,
                                   current_user = Depends(get_current_user),
                                   service: WorkoutPlanService = Depends(get_workout_plan_service)):
    try:
        if trainer_id:
            plans = await service.get_workout_plans_by_trainer_and_client(trainer_id, current_user["id"])
        else:
            plans = await service.get_workout_plans_by_client(current_user["id"])
        return plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plan_id}", response_model=WorkoutPlanResponse, dependencies=[Depends(get_current_user)])
async def get_workout_plan(plan_id: str, service: WorkoutPlanService = Depends(get_workout_plan_service)):
    try:
        plan = await service.get_by_id(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Workout plan not found")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#------------------------------Admin routes------------------------------

@router.get("/", response_model=list[WorkoutPlanResponse], dependencies=[Depends(get_current_admin)])
async def get_all_workout_plans(service: WorkoutPlanService = Depends(get_workout_plan_service)):
    try:
        return await service.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
