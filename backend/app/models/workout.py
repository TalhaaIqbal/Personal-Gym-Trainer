from pydantic import BaseModel
from datetime import date, time
from ..helper.object_id_validate import PyProjectID

class Exercise(BaseModel):
    name: str
    muscle_group: Literal["chest", "back", "legs", "shoulders", "bicep", "tricep", "cardio", "core", "mixed"]
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