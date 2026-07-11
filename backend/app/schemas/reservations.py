from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from app.models.reservations import RecurringType, ReservationStatus

class RecurringRuleIn(BaseModel):
    type: RecurringType
    interval: int = 1
    end_date: datetime

class ServiceIn(BaseModel):
    service_id: int

class ReservationCreate(BaseModel):
    space_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    start_time: datetime
    end_time: datetime
    services: List[ServiceIn] = []
    recurring: Optional[RecurringRuleIn] = None
    sync_google_calendar: bool = False  # korisnik bira hoće li sync
    notes: Optional[str] = None

class ReservationOut(BaseModel):
    id: int
    space_id: int
    first_name: str
    last_name: str
    email: str
    start_time: datetime
    end_time: datetime
    total_price: float
    status: ReservationStatus
    google_event_id: Optional[str]

    class Config:
        from_attributes = True

# Za prikaz sažetka PRIJE potvrde (preview korak)
class ReservationPreview(BaseModel):
    space_name: str
    start_time: datetime
    end_time: datetime
    hours: float
    price_per_hour: float
    services_total: float
    total_price: float
    recurring_dates: Optional[List[datetime]] = None