import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, time
from typing import Optional

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    def __init__(self):
        self.service = None

    def get_credentials(self, token_json: Optional[str] = None) -> Credentials:
        if token_json:
            return Credentials.from_authorized_user_info(token_json, SCOPES)
        return None

    def get_flow(self) -> Flow:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")]
                }
            },
            SCOPES
        )
        return flow
    
    def build_service(self, credentials: Credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
        return self.service
    
    def _build_event_dict(self, summary: str, start_datetime: datetime, end_datetime: datetime, description: str = "", location: str = "") -> dict:
        return {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_datetime.isoformat(),
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
            },
        }
    
    def create_event(self, 
                     summary: str,
                     start_datetime: datetime,
                     end_datetime: datetime,
                     description: str = "",
                     location: str = "") -> str:
        if not self.service:
            raise ValueError("Calendar service not initialized")
        
        event = self._build_event_dict(summary, start_datetime, end_datetime, description, location)
        event_result = self.service.events().insert(calendarId='primary', body=event).execute()
        return event_result['id']
    
    def update_event(self,
                     event_id: str,
                     summary: str,
                     start_datetime: datetime,
                     end_datetime: datetime,
                     description: str = "",
                     location: str = "") -> str:
        if not self.service:
            raise ValueError("Calendar service not initialized")
        
        event = self._build_event_dict(summary, start_datetime, end_datetime, description, location)
        event_result = self.service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        return event_result['id']
    
    def delete_event(self, event_id: str):
        if not self.service:
            raise ValueError("Calendar service not initialized")
        
        self.service.events().delete(calendarId='primary', eventId=event_id).execute()
