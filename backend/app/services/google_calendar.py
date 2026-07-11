from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")  # email SUMIT kalendara
CREDENTIALS_FILE = "credentials.json"

def get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)

def create_calendar_event(
    title: str,
    start: datetime,
    end: datetime,
    description: str,
    attendee_email: str = None
) -> str:
    service = get_calendar_service()

    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": "Europe/Sarajevo"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Europe/Sarajevo"},
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24 * 60},  # dan prije
                {"method": "popup", "minutes": 60},        # sat prije
            ],
        },
    }

    # Dodaj korisnika kao attendee ako je pristao na sinkronizaciju
    if attendee_email:
        event["attendees"] = [{"email": attendee_email}]

    result = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event,
        sendUpdates="all"  # šalje email invite attendeeu
    ).execute()

    return result["id"]  # vraćamo google_event_id

def delete_calendar_event(event_id: str):
    service = get_calendar_service()
    service.events().delete(
        calendarId=CALENDAR_ID,
        eventId=event_id
    ).execute()