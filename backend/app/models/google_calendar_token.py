from pydantic import BaseModel
from ..helper.object_id_validate import PyProjectID

class GoogleCalendarToken(BaseModel):
    user_id: PyProjectID
    google_token: str
    calendar_enabled: bool = True
