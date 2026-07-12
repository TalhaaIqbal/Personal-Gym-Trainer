from pydantic import BaseModel, field_validator, model_validator
from datetime import date
from typing import Literal, List, Optional

def validate_date(date: date) -> None:
    if date < date.today():
        raise ValueError("Date cannot be in the past")

class ExerciseCreate(BaseModel):
    name: str
    muscle_groups: List[Literal["chest", "back", "legs", "shoulders", "bicep", "tricep", "cardio", "core", "mixed"]]
    sets: int
    reps: str
    weight: Optional[str] = None
    duration: Optional[str] = None
    rest_time: Optional[str] = None
    notes: Optional[str] = None
    video_key: Optional[str] = None

class WorkoutDayCreate(BaseModel):
    date: date
    is_rest_day: bool = False
    exercises: List[ExerciseCreate] = []

class WorkoutPlanCreate(BaseModel):  #Main
    client_id: str
    name: str
    description: Optional[str] = None
    days: List[WorkoutDayCreate]
    start_date: date
    end_date: Optional[date] = None

    @field_validator('start_date')
    def validate_start_date(cls, v):
        validate_date(v)
        return v

    @field_validator('end_date')
    def validate_end_date(cls, v):
        if v and v < date.today():
            raise ValueError("End date cannot be in the past")
        return v

    @model_validator(mode='after')
    def validate_date_order(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date")
        return self

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    muscle_groups: Optional[List[Literal["chest", "back", "legs", "shoulders", "bicep", "tricep", "cardio", "core", "mixed"]]]
    sets: Optional[int] = None
    reps: Optional[str] = None
    weight: Optional[str] = None
    duration: Optional[str] = None
    rest_time: Optional[str] = None
    notes: Optional[str] = None
    video_key: Optional[str] = None

class WorkoutDayUpdate(BaseModel):
    date: Optional[date] = None
    is_rest_day: Optional[bool] = None
    exercises: Optional[List[ExerciseUpdate]] = None

class WorkoutPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    days: Optional[List[WorkoutDayUpdate]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[Literal["active", "completed", "archived"]] = None

    @field_validator('start_date')
    def validate_start_date(cls, v):
        if v:
            validate_date(v)
        return v

    @field_validator('end_date')
    def validate_end_date(cls, v):
        if v and v < date.today():
            raise ValueError("End date cannot be in the past")
        return v

    @model_validator(mode='after')
    def validate_date_order(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date")
        return self

class ExerciseResponse(BaseModel):
    name: str
    muscle_groups: List[Literal["chest", "back", "legs", "shoulders", "bicep", "tricep", "cardio", "core", "mixed"]]
    sets: int
    reps: str
    weight: Optional[str] = None
    duration: Optional[str] = None
    rest_time: Optional[str] = None
    notes: Optional[str] = None
    video_key: Optional[str] = None

class WorkoutDayResponse(BaseModel):
    date: str
    is_rest_day: bool
    exercises: List[ExerciseResponse]

class WorkoutPlanResponse(BaseModel):
    id: str
    trainer_id: str
    client_id: str
    name: str
    description: Optional[str] = None
    days: List[WorkoutDayResponse]
    start_date: str
    end_date: Optional[str] = None
    status: Literal["active", "completed", "archived"] = "active"