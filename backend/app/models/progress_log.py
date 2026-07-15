from pydantic import BaseModel
from datetime import date, time
from ..helper.object_id_validate import PyProjectID

class ProgressLog(BaseModel):
    client_id: PyProjectID
    booking_date: date
    weight_kg: float | None = None
    notes: str | None = None
    workout_completed: bool = False