from fastapi import APIRouter, Depends, HTTPException, Query ,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List
from app.models.spaces import Space, SpaceImage, SpaceEquipment
from app.models.reservations import Reservation, ReservationStatus, SpaceService
from app.schemas.spaces import SpaceCreate, SpaceOut
from app.schemas.user import AdminCreate
from app.services.email import send_cancellation_email
from app.services.google_calendar import delete_calendar_event
import os
from app.services.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
    get_current_admin,
)
from app.database import get_db
from app.models.users import User
router = APIRouter(prefix="/admin", tags=["Administracija"])

@router.get("/me")
def get_me(
    current_admin: User = Depends(get_current_admin),
):
    return {
        "id": current_admin.id,
        "username": current_admin.username,
        "role": current_admin.role,
    }

@router.post(
    "/create-admin",
    status_code=status.HTTP_201_CREATED,
)
def create_admin(
    admin_data: AdminCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    filters = [User.username == admin_data.username]

    if admin_data.email:
        filters.append(User.email == admin_data.email)

    existing_user = (
        db.query(User)
        .filter(or_(*filters))
        .first()
    )

    if existing_user:
        if existing_user.username == admin_data.username:
            detail = "Korisničko ime već postoji."
        else:
            detail = "Email adresa već postoji."

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    new_admin = User(
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=get_password_hash(admin_data.password),
        role="admin",
        is_active=True,
    )

    try:
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Korisničko ime ili email već postoji.",
        )

    return {
        "message": "Administrator je uspješno kreiran.",
        "admin": {
            "id": new_admin.id,
            "username": new_admin.username,
            "email": new_admin.email,
            "role": new_admin.role,
            "is_active": new_admin.is_active,
        },
    }

# ─── AUTH ────────────────────────────────────────────────────────────────────

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Pogrešno korisničko ime ili lozinka",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Pogrešno korisničko ime ili lozinka",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Korisnički račun nije aktivan",
        )

    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Korisnik nema administratorska prava",
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        },
    }

# ─── PROSTORI ─────────────────────────────────────────────────────────────────

@router.get("/spaces", response_model=List[SpaceOut])
def get_spaces(
    search: Optional[str] = Query(
        default=None,
        description="Pretraga prostora po nazivu",
    ),
    space_type: Optional[str] = Query(
        default=None,
        description="Filtriranje po vrsti prostora",
    ),
    min_capacity: Optional[int] = Query(
        default=None,
        ge=1,
        description="Minimalni kapacitet prostora",
    ),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    query = db.query(Space)

    if search:
        query = query.filter(
            Space.name.ilike(f"%{search.strip()}%")
        )

    if space_type:
        query = query.filter(
            Space.space_type == space_type
        )

    if min_capacity is not None:
        query = query.filter(
            Space.capacity >= min_capacity
        )

    spaces = query.order_by(Space.name.asc()).all()

    return spaces


@router.get("/spaces/{space_id}", response_model=SpaceOut)
def get_space(
    space_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    space = (
        db.query(Space)
        .filter(Space.id == space_id)
        .first()
    )

    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prostor nije pronađen",
        )

    return space

@router.put("/spaces/{space_id}", response_model=SpaceOut)
def update_space(
    space_id: int,
    data: SpaceCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Prostor nije pronađen")

    space.name = data.name
    space.description = data.description
    space.capacity = data.capacity
    space.price_per_hour = data.price_per_hour
    space.space_type = data.space_type

    # Obnovi slike i opremu
    db.query(SpaceImage).filter(SpaceImage.space_id == space_id).delete()
    db.query(SpaceEquipment).filter(SpaceEquipment.space_id == space_id).delete()

    for img in data.images:
        db.add(SpaceImage(space_id=space_id, url=img.url, is_primary=img.is_primary))
    for eq in data.equipment:
        db.add(SpaceEquipment(space_id=space_id, name=eq.name))

    db.commit()
    db.refresh(space)
    return space


@router.delete("/spaces/{space_id}")
def delete_space(
    space_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Prostor nije pronađen")

    # Provjeri ima li aktivnih rezervacija
    active = db.query(Reservation).filter(
        Reservation.space_id == space_id,
        Reservation.status == ReservationStatus.confirmed,
        Reservation.end_time > datetime.utcnow()
    ).first()

    if active:
        raise HTTPException(
            status_code=400,
            detail="Ne možete obrisati prostor s aktivnim rezervacijama"
        )

    db.delete(space)
    db.commit()
    return {"message": f"Prostor '{space.name}' je obrisan"}


# ─── REZERVACIJE ──────────────────────────────────────────────────────────────

@router.get("/reservations")
def get_reservations(
    status: Optional[str] = Query(None),
    space_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    query = db.query(Reservation)

    if status:
        query = query.filter(Reservation.status == status)
    if space_id:
        query = query.filter(Reservation.space_id == space_id)
    if from_date:
        query = query.filter(Reservation.start_time >= from_date)
    if to_date:
        query = query.filter(Reservation.end_time <= to_date)
    if search:
        query = query.filter(
            (Reservation.first_name.ilike(f"%{search}%")) |
            (Reservation.last_name.ilike(f"%{search}%")) |
            (Reservation.email.ilike(f"%{search}%")) |
            (Reservation.company.ilike(f"%{search}%"))
        )

    reservations = query.order_by(Reservation.start_time.desc()).all()
    return reservations


@router.patch("/reservations/{reservation_id}/confirm")
def confirm_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Rezervacija nije pronađena")
    if reservation.status != ReservationStatus.pending:
        raise HTTPException(status_code=400, detail="Rezervacija nije u statusu čekanja")

    reservation.status = ReservationStatus.confirmed
    db.commit()
    return {"message": f"Rezervacija #{reservation_id} je potvrđena"}


@router.patch("/reservations/{reservation_id}/cancel")
async def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Rezervacija nije pronađena")
    if reservation.status == ReservationStatus.cancelled:
        raise HTTPException(status_code=400, detail="Rezervacija je već otkazana")

    space = db.query(Space).filter(Space.id == reservation.space_id).first()

    reservation.status = ReservationStatus.cancelled
    db.commit()

    # Obrisi iz Google Calendara
    if reservation.google_event_id:
        try:
            delete_calendar_event(reservation.google_event_id)
        except Exception as e:
            print(f"Google Calendar greška: {e}")

    # Pošalji email o otkazivanju
    await send_cancellation_email(
        email=reservation.email,
        first_name=reservation.first_name,
        space_name=space.name,
        start_time=reservation.start_time,
        reservation_id=reservation.id,
    )

    return {"message": f"Rezervacija #{reservation_id} je otkazana"}


# ─── IZVJEŠTAJI ───────────────────────────────────────────────────────────────

@router.get("/reports")
def get_reports(
    from_date: datetime = Query(...),
    to_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    # Samo potvrđene rezervacije
    base_query = db.query(Reservation).filter(
        Reservation.status == ReservationStatus.confirmed,
        Reservation.start_time >= from_date,
        Reservation.end_time <= to_date,
    )

    reservations = base_query.all()
    total_revenue = sum(r.total_price for r in reservations)
    total_reservations = len(reservations)

    # Korištenost po prostoru
    space_stats = []
    spaces = db.query(Space).all()
    for space in spaces:
        space_reservations = [r for r in reservations if r.space_id == space.id]
        space_hours = sum(
            (r.end_time - r.start_time).seconds / 3600
            for r in space_reservations
        )
        space_revenue = sum(r.total_price for r in space_reservations)
        space_stats.append({
            "space_id": space.id,
            "space_name": space.name,
            "total_reservations": len(space_reservations),
            "total_hours": round(space_hours, 1),
            "total_revenue": round(space_revenue, 2),
        })

    return {
        "period": {
            "from": from_date,
            "to": to_date,
        },
        "summary": {
            "total_revenue": round(total_revenue, 2),
            "total_reservations": total_reservations,
        },
        "by_space": space_stats,
    }