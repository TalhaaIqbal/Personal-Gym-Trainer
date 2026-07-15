from pydantic import BaseModel
from datetime import date, time
from ..helper.object_id_validate import PyProjectID

class Availability(BaseModel):
    id: PyProjectID
    trainer_id: PyProjectID
    booking_date: date
    start_time: time
    end_time: time