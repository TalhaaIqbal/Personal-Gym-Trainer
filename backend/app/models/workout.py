from pydantic import BaseModel, BeforeValidator
from typing import Annotated, Literal, List
from bson import ObjectId

def validate_object_id(v: str) -> str:
    if ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid Object ID")

PyProjectID = Annotated[str, BeforeValidator(validate_object_id)]

class Exercise(BaseModel):
    name: str
    muscle_group: Literal["chest", "back", "legs", "shoulders", "arms", "cardio", "core", "mixed"]
    sets: int
    reps: int
    notes: str | None = None

class WorkoutDay(BaseModel):
    day_label: str
    exercises: List[Exercise]

class WorkoutPlan(BaseModel):
    trainer_id: PyProjectID
    client_id: PyProjectID
    title: str
    description: str | None = None
    weeks: list[list[WorkoutDay]]