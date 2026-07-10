from pydantic import BaseModel, field_validator, model_validator
from datetime import date
from typing import Literal, List

def validate_date(date: date) -> None:
    if date < date.today():
        raise ValueError("Date cannot be in the past")

class ExerciseCreate(BaseModel):
    name: str
    sets: int
    reps: str
    weight: str | None = None
    duration: str | None = None
    rest_time: str | None = None
    notes: str | None = None

class WorkoutPlanCreate(BaseModel):
    client_id: str
    name: str
    description: str | None = None
    exercises: List[ExerciseCreate]
    start_date: date
    end_date: date | None = None

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
    name: str | None = None
    sets: int | None = None
    reps: str | None = None
    weight: str | None = None
    duration: str | None = None
    rest_time: str | None = None
    notes: str | None = None

class WorkoutPlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    exercises: List[ExerciseUpdate] | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: Literal["active", "completed", "archived"] | None = None

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
    sets: int
    reps: str
    weight: str | None = None
    duration: str | None = None
    rest_time: str | None = None
    notes: str | None = None

class WorkoutPlanResponse(BaseModel):
    id: str
    trainer_id: str
    client_id: str
    name: str
    description: str | None = None
    exercises: List[ExerciseResponse]
    start_date: str
    end_date: str | None = None
    status: Literal["active", "completed", "archived"] = "active"
