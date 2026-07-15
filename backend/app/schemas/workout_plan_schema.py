from pydantic import BaseModel, field_validator, model_validator, Field, ConfigDict
from datetime import date
from typing import Literal, List, Optional
from typing_extensions import Annotated
from ..helper.date_time_validate import validate_date

MUSCLE_GROUP = Literal["chest", "back", "legs", "shoulders", "bicep", "tricep", "cardio", "core", "mixed"]
WORKOUT_STATUS = Literal["active", "completed", "archived"]
MuscleGroups = List[MUSCLE_GROUP]

class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Exercise name")
    muscle_groups: MuscleGroups = Field(..., description="Target muscle groups")
    sets: int = Field(..., gt=0, description="Number of sets")
    reps: str = Field(..., description="Reps (e.g., '8-12', '10')")
    weight: Optional[str] = Field(None, description="Weight (e.g., '50kg', 'bodyweight')")
    duration: Optional[str] = Field(None, description="Duration for cardio exercises")
    rest_time: Optional[str] = Field(None, description="Rest time between sets")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    video_key: Optional[str] = Field(None, description="Video reference key")

class ExerciseCreate(ExerciseBase):
    pass

class WorkoutDayCreate(BaseModel):
    date: Annotated[date, Field(description="Workout date")]
    is_rest_day: bool = Field(default=False, description="Whether this is a rest day")
    exercises: List[ExerciseCreate] = Field(default_factory=list, description="List of exercises")
    
    @model_validator(mode='after')
    def validate_rest_day_exercises(self):
        if self.is_rest_day and self.exercises:
            self.exercises = []
        return self

class WorkoutPlanCreate(BaseModel):
    client_id: str = Field(..., min_length=1, description="Client ID")
    name: str = Field(..., min_length=1, max_length=100, description="Plan name")
    description: Optional[str] = Field(None, max_length=500, description="Plan description")
    days: List[WorkoutDayCreate] = Field(..., min_length=1, description="Workout days")
    start_date: Annotated[date, Field(description="Plan start date")]
    end_date: Optional[date] = Field(None, description="Plan end date")

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v: date) -> date:
        validate_date(v)
        return v

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[date]) -> Optional[date]:
        if v and v < date.today():
            raise ValueError("End date cannot be in the past")
        return v

    @model_validator(mode='after')
    def validate_date_order(self) -> 'WorkoutPlanCreate':
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date")
        return self


class ExerciseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    muscle_groups: Optional[MuscleGroups] = None
    sets: Optional[int] = Field(None, gt=0)
    reps: Optional[str] = None
    weight: Optional[str] = None
    duration: Optional[str] = None
    rest_time: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)
    video_key: Optional[str] = None

class WorkoutDayUpdate(BaseModel):
    date: Optional[date] = None
    is_rest_day: Optional[bool] = None
    exercises: Optional[List[ExerciseUpdate]] = None
    
    @model_validator(mode='after')
    def validate_rest_day_exercises(self) -> 'WorkoutDayUpdate':
        if self.is_rest_day and self.exercises:
            self.exercises = []
        return self

class WorkoutPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    days: Optional[List[WorkoutDayUpdate]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[WORKOUT_STATUS] = None

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v: Optional[date]) -> Optional[date]:
        if v:
            validate_date(v)
        return v

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[date]) -> Optional[date]:
        if v and v < date.today():
            raise ValueError("End date cannot be in the past")
        return v

    @model_validator(mode='after')
    def validate_date_order(self) -> 'WorkoutPlanUpdate':
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date")
        return self

class ExerciseResponse(ExerciseBase):
    id: Optional[str] = Field(None, description="Exercise ID")
    

class WorkoutDayResponse(BaseModel):
    id: Optional[str] = Field(None, description="Workout day ID")
    date: str = Field(..., description="Workout date (ISO format)")
    is_rest_day: bool = Field(..., description="Whether this is a rest day")
    exercises: List[ExerciseResponse] = Field(default_factory=list, description="List of exercises")
    

class WorkoutPlanResponse(BaseModel):
    id: str = Field(..., description="Workout plan ID")
    trainer_id: str = Field(..., description="Trainer ID")
    client_id: str = Field(..., description="Client ID")
    name: str = Field(..., description="Plan name")
    description: Optional[str] = Field(None, description="Plan description")
    days: List[WorkoutDayResponse] = Field(default_factory=list, description="Workout days")
    start_date: str = Field(..., description="Start date (ISO format)")
    end_date: Optional[str] = Field(None, description="End date (ISO format)")
    status: WORKOUT_STATUS = Field(default="active", description="Plan status")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True