from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.services.email import send_reservation_confirmation
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from app.database import get_db
from app.models.reservations import Reservation, ReservationService, RecurringRule, ReservationStatus, SpaceService
from app.models.spaces import Space
from app.schemas.reservations import ReservationCreate, ReservationOut, ReservationPreview
from app.services.google_calendar import create_calendar_event

router = APIRouter(prefix="/reservations", tags=["Rezervacije"])


def check_overlap(db: Session, space_id: int, start: datetime, end: datetime, exclude_id: int = None):
    """Provjeri da li se termin preklapa s postojećim rezervacijama."""
    query = db.query(Reservation).filter(
        Reservation.space_id == space_id,
        Reservation.status != ReservationStatus.cancelled,
        Reservation.start_time < end,
        Reservation.end_time > start,
    )
    if exclude_id:
        query = query.filter(Reservation.id != exclude_id)
    return query.first()


def generate_recurring_dates(start, end, rule) -> List:
    """Generiraj sve termine za ponavljajuću rezervaciju."""
    dates = []
    current_start = start
    current_end = end
    duration = end - start

    while current_start <= rule.end_date:
        dates.append((current_start, current_end))
        if rule.type == "daily":
            current_start += timedelta(days=rule.interval)
        else:  # weekly
            current_start += timedelta(weeks=rule.interval)
        current_end = current_start + duration

    return dates


@router.post("/preview", response_model=ReservationPreview)
def preview_reservation(data: ReservationCreate, db: Session = Depends(get_db)):
    """Sažetak rezervacije prije potvrde — nikad ne piše u bazu."""
    space = db.query(Space).filter(Space.id == data.space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Prostor nije pronađen")

    hours = (data.end_time - data.start_time).seconds / 3600
    space_price = hours * space.price_per_hour

    services_total = 0.0
    for s in data.services:
        svc = db.query(SpaceService).filter(SpaceService.id == s.service_id).first()
        if svc:
            services_total += svc.price

    recurring_dates = None
    if data.recurring:
        dates = generate_recurring_dates(data.start_time, data.end_time, data.recurring)
        recurring_dates = [d[0] for d in dates]

    return ReservationPreview(
        space_name=space.name,
        start_time=data.start_time,
        end_time=data.end_time,
        hours=hours,
        price_per_hour=space.price_per_hour,
        services_total=services_total,
        total_price=(space_price + services_total) * (len(recurring_dates) if recurring_dates else 1),
        recurring_dates=recurring_dates,
    )


@router.post("/", response_model=List[ReservationOut])
async def create_reservation(
    data: ReservationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    space = db.query(Space).filter(Space.id == data.space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Prostor nije pronađen")

    hours = (data.end_time - data.start_time).seconds / 3600
    space_price = hours * space.price_per_hour

    # Izračunaj cijenu usluga
    services_data = []
    services_total = 0.0
    for s in data.services:
        svc = db.query(SpaceService).filter(SpaceService.id == s.service_id).first()
        if not svc:
            raise HTTPException(status_code=404, detail=f"Usluga {s.service_id} nije pronađena")
        services_data.append(svc)
        services_total += svc.price

    total_price = space_price + services_total

    # Generiraj termine (jedan ili više ako je recurring)
    if data.recurring:
        rule = RecurringRule(
            type=data.recurring.type,
            interval=data.recurring.interval,
            end_date=data.recurring.end_date,
        )
        db.add(rule)
        db.flush()
        dates = generate_recurring_dates(data.start_time, data.end_time, data.recurring)
    else:
        rule = None
        dates = [(data.start_time, data.end_time)]

    created = []
    for start, end in dates:
        # Provjeri preklapanje za svaki termin
        if check_overlap(db, data.space_id, start, end):
            raise HTTPException(
                status_code=409,
                detail=f"Termin {start} - {end} je već zauzet"
            )

        reservation = Reservation(
            space_id=data.space_id,
            recurring_rule_id=rule.id if rule else None,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            company=data.company,
            start_time=start,
            end_time=end,
            total_price=total_price,
            notes=data.notes,
            status=ReservationStatus.pending,
        )
        db.add(reservation)
        db.flush()

        for svc in services_data:
            db.add(ReservationService(
                reservation_id=reservation.id,
                service_id=svc.id,
                price_at_booking=svc.price,
            ))

        # Google Calendar sinkronizacija
        try:
            description = (
                f"Rezervacija: {space.name}\n"
                f"Korisnik: {data.first_name} {data.last_name}\n"
                f"Kontakt: {data.email} | {data.phone}\n"
                f"Ukupna cijena: {total_price} KM"
            )
            event_id = create_calendar_event(
                title=f"Rezervacija - {space.name}",
                start=start,
                end=end,
                description=description,
                attendee_email=data.email if data.sync_google_calendar else None,
            )
            reservation.google_event_id = event_id
        except Exception as e:
            print(f"Google Calendar greška: {e}")

        created.append(reservation)

    db.commit()
    for r in created:
        db.refresh(r)

    # Slanje email potvrde u pozadini
    background_tasks.add_task(
        send_reservation_confirmation,
        email=data.email,
        first_name=data.first_name,
        space_name=space.name,
        start_time=created[0].start_time,
        end_time=created[0].end_time,
        total_price=sum(r.total_price for r in created),
        reservation_id=created[0].id,
    )

    return created