from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models.spaces import Space
from app.models.reservations import Reservation, ReservationStatus

router = APIRouter(prefix="/availability", tags=["Dostupnost"])


@router.get("/spaces")
def get_available_spaces(
    from_date: datetime = Query(..., description="Od datuma"),
    to_date: datetime = Query(..., description="Do datuma"),
    space_type: Optional[str] = Query(None, description="Vrsta prostora"),
    capacity: Optional[int] = Query(None, description="Minimalni kapacitet"),
    db: Session = Depends(get_db)
):
    """
    Lista dostupnih prostora s filterima.
    Vraća prostore koji NISU zauzeti u traženom periodu.
    """
    # Zauzeti prostori u traženom periodu
    busy_space_ids = db.query(Reservation.space_id).filter(
        Reservation.status != ReservationStatus.cancelled,
        Reservation.start_time < to_date,
        Reservation.end_time > from_date,
    ).subquery()

    query = db.query(Space).filter(Space.id.notin_(busy_space_ids))

    if space_type:
        query = query.filter(Space.space_type == space_type)
    if capacity:
        query = query.filter(Space.capacity >= capacity)

    spaces = query.all()

    return [
        {
            "id": space.id,
            "name": space.name,
            "description": space.description,
            "capacity": space.capacity,
            "price_per_hour": space.price_per_hour,
            "space_type": space.space_type,
            "images": [{"url": img.url, "is_primary": img.is_primary} for img in space.images],
            "equipment": [{"name": eq.name} for eq in space.equipment],
        }
        for space in spaces
    ]


@router.get("/spaces/{space_id}/calendar")
def get_space_calendar(
    space_id: int,
    from_date: datetime = Query(..., description="Od datuma"),
    to_date: datetime = Query(..., description="Do datuma"),
    db: Session = Depends(get_db)
):
    """
    Zauzeti termini za jedan prostor u traženom periodu.
    Frontend koristi ovo za prikaz kalendara zauzetosti.
    """
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        return {"detail": "Prostor nije pronađen"}

    reservations = db.query(Reservation).filter(
        Reservation.space_id == space_id,
        Reservation.status != ReservationStatus.cancelled,
        Reservation.start_time < to_date,
        Reservation.end_time > from_date,
    ).order_by(Reservation.start_time).all()

    busy_slots = [
        {
            "reservation_id": r.id,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "status": r.status,
        }
        for r in reservations
    ]

    return {
        "space_id": space_id,
        "space_name": space.name,
        "period": {
            "from": from_date,
            "to": to_date,
        },
        "busy_slots": busy_slots,
        "total_busy": len(busy_slots),
    }