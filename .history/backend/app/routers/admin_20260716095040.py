from datetime import datetime
import os
from typing import List, Optional,Annotated
import shutil
from pathlib import Path
from uuid import uuid4
from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    Query,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reservations import (
    Reservation,
    ReservationStatus,
    SpaceService,
)
from app.models.spaces import (
    Space,
    SpaceEquipment,
    SpaceImage,
)
from app.models.users import User
from app.schemas.spaces import (
    SpaceCreate,
    SpaceOut,
)
from app.schemas.user import AdminCreate
from app.services.auth import (
    create_access_token,
    get_current_admin,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.services.email import send_cancellation_email
from app.services.google_calendar import delete_calendar_event
router = APIRouter(prefix="/admin", tags=["Administracija"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

UPLOAD_ROOT = Path("/app/uploads/spaces")
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


@router.post(
    "/spaces/{space_id}/images",
    status_code=status.HTTP_201_CREATED,
)
async def upload_space_images(
    space_id: int,
    images: Annotated[
        list[UploadFile],
        File(description="JPG, PNG ili WEBP slike prostora"),
    ],
    primary_index: int = 0,
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
            detail="Prostor nije pronađen.",
        )

    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nije odabrana nijedna slika.",
        )

    if len(images) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Možete učitati najviše 10 slika odjednom.",
        )

    if primary_index < 0 or primary_index >= len(images):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Neispravan indeks glavne slike.",
        )

    space_directory = UPLOAD_ROOT / str(space_id)
    space_directory.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    created_images = []

    try:
        # Ukloni oznaku glavne slike sa svih postojećih slika.
        db.query(SpaceImage).filter(
            SpaceImage.space_id == space_id,
            SpaceImage.is_primary.is_(True),
        ).update(
            {"is_primary": False},
            synchronize_session=False,
        )

        for index, image in enumerate(images):
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Datoteka '{image.filename}' "
                        "nije podržan format slike."
                    ),
                )

            image.file.seek(0, os.SEEK_END)
            file_size = image.file.tell()
            image.file.seek(0)

            if file_size > MAX_IMAGE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Datoteka '{image.filename}' "
                        "je veća od 5 MB."
                    ),
                )

            suffix = Path(
                image.filename or "",
            ).suffix.lower()

            if suffix not in {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
            }:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Datoteka '{image.filename}' "
                        "ima neispravnu ekstenziju."
                    ),
                )

            generated_filename = (
                f"{uuid4().hex}{suffix}"
            )

            file_path = (
                space_directory /
                generated_filename
            )

            with file_path.open("wb") as buffer:
                shutil.copyfileobj(
                    image.file,
                    buffer,
                )

            saved_paths.append(file_path)

            relative_url = (
                f"/uploads/spaces/"
                f"{space_id}/"
                f"{generated_filename}"
            )

            db_image = SpaceImage(
                space_id=space_id,
                url=relative_url,
                is_primary=index == primary_index,
            )

            db.add(db_image)
            created_images.append(db_image)

        db.commit()

        for db_image in created_images:
            db.refresh(db_image)

        return {
            "message": "Slike su uspješno spremljene.",
            "images": [
                {
                    "id": db_image.id,
                    "url": db_image.url,
                    "is_primary": db_image.is_primary,
                }
                for db_image in created_images
            ],
        }

    except Exception:
        db.rollback()

        for file_path in saved_paths:
            if file_path.exists():
                file_path.unlink()

        raise

    finally:
        for image in images:
            await image.close()

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

@router.post(
    "/spaces",
    response_model=SpaceOut,
    status_code=status.HTTP_201_CREATED,
)
def create_space(
    data: SpaceCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):

    existing_space = (
        db.query(Space)
        .filter(
            func.lower(Space.name)
            == data.name.strip().lower()
        )
        .first()
    )

    if existing_space:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Prostor s tim nazivom već postoji.",
        )

    space = Space(
        name=data.name.strip(),
        description=data.description,
        name_en=data.name_en,
        description_en=data.description_en,
        space_type=data.space_type,
        space_subtype=data.space_subtype,
        capacity=data.capacity,
        price=data.price,
        price_unit=data.price_unit,
        is_modular=data.is_modular,
        combination_group=(
            data.combination_group
            if data.is_modular
            else None
        ),
    )

    try:
        db.add(space)
        db.flush()

        for image in data.images:
            db.add(
                SpaceImage(
                    space_id=space.id,
                    url=image.url,
                    is_primary=image.is_primary,
                )
            )

        for equipment in data.equipment:
            db.add(
                SpaceEquipment(
                    space_id=space.id,
                    name=equipment.name,
                )
            )

        for service in data.services:
            db.add(
                SpaceService(
                    space_id=space.id,
                    name=service.name,
                    name_en=service.name_en,
                    description=service.description,
                    description_en=service.description_en,
                    price=service.price,
                    conditions=service.conditions,
                )
            )

        db.commit()
        db.refresh(space)

        return space

    except Exception:
        db.rollback()
        raise

@router.get(
    "/spaces",
    response_model=List[SpaceOut],
)
def get_spaces(
    search: Optional[str] = Query(
        default=None,
        description="Pretraga po hrvatskom ili engleskom nazivu i opisu",
    ),
    space_type: Optional[str] = Query(
        default=None,
        description="Filtriranje po glavnoj vrsti prostora",
    ),
    space_subtype: Optional[str] = Query(
        default=None,
        description="Filtriranje po podvrsti prostora",
    ),
    min_capacity: Optional[int] = Query(
        default=None,
        ge=1,
        description="Minimalni kapacitet prostora",
    ),
    max_capacity: Optional[int] = Query(
        default=None,
        ge=1,
        description="Maksimalni kapacitet prostora",
    ),
    is_modular: Optional[bool] = Query(
        default=None,
        description="Filtriranje modularnih dvorana",
    ),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    query = db.query(Space)

    if search:
        search_value = search.strip()

        if search_value:
            search_pattern = f"%{search_value}%"

            query = query.filter(
                or_(
                    Space.name.ilike(search_pattern),
                    Space.name_en.ilike(search_pattern),
                    Space.description.ilike(search_pattern),
                    Space.description_en.ilike(search_pattern),
                )
            )

    if space_type:
        query = query.filter(
            Space.space_type == space_type
        )

    if space_subtype:
        query = query.filter(
            Space.space_subtype == space_subtype
        )

    if min_capacity is not None:
        query = query.filter(
            Space.capacity >= min_capacity
        )

    if max_capacity is not None:
        query = query.filter(
            Space.capacity <= max_capacity
        )

    if (
        min_capacity is not None
        and max_capacity is not None
        and min_capacity > max_capacity
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Minimalni kapacitet ne može biti veći "
                "od maksimalnog kapaciteta."
            ),
        )

    if is_modular is not None:
        query = query.filter(
            Space.is_modular == is_modular
        )

    return query.order_by(Space.name.asc()).all()


@router.get(
    "/spaces/{space_id}",
    response_model=SpaceOut,
)
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
            detail="Prostor nije pronađen.",
        )

    return space


@router.put(
    "/spaces/{space_id}",
    response_model=SpaceOut,
)
def update_space(
    space_id: int,
    data: SpaceCreate,
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
            detail="Prostor nije pronađen.",
        )

    validate_space_data(data)

    try:
        space.name = data.name
        space.description = data.description
        space.name_en = data.name_en
        space.description_en = data.description_en

        space.space_type = data.space_type
        space.space_subtype = data.space_subtype

        space.capacity = data.capacity
        space.price = data.price
        space.price_unit = data.price_unit

        space.is_modular = data.is_modular
        space.combination_group = (
            data.combination_group
            if data.is_modular
            else None
        )

        # Brišemo stare povezane podatke i unosimo nove.
        db.query(SpaceImage).filter(
            SpaceImage.space_id == space_id
        ).delete(synchronize_session=False)

        db.query(SpaceEquipment).filter(
            SpaceEquipment.space_id == space_id
        ).delete(synchronize_session=False)

        db.query(SpaceService).filter(
            SpaceService.space_id == space_id
        ).delete(synchronize_session=False)

        for image in data.images:
            db.add(
                SpaceImage(
                    space_id=space_id,
                    url=image.url,
                    is_primary=image.is_primary,
                )
            )

        for equipment in data.equipment:
            db.add(
                SpaceEquipment(
                    space_id=space_id,
                    name=equipment.name,
                )
            )

        for service in data.services:
            db.add(
                SpaceService(
                    space_id=space_id,
                    name=service.name,
                    name_en=service.name_en,
                    description=service.description,
                    description_en=service.description_en,
                    price=service.price,
                    conditions=service.conditions,
                )
            )

        db.commit()
        db.refresh(space)

        return space

    except Exception:
        db.rollback()
        raise


@router.delete("/spaces/{space_id}")
def delete_space(
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
            detail="Prostor nije pronađen.",
        )

    active_reservation = (
        db.query(Reservation)
        .filter(
            Reservation.space_id == space_id,
            Reservation.status
            == ReservationStatus.confirmed,
            Reservation.end_time > datetime.utcnow(),
        )
        .first()
    )

    if active_reservation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Nije moguće obrisati prostor koji ima "
                "aktivne buduće rezervacije."
            ),
        )

    space_name = space.name
    space_directory = UPLOAD_ROOT / str(space_id)

    try:
        db.delete(space)
        db.commit()

    except Exception:
        db.rollback()
        raise

    try:
        if space_directory.exists():
            shutil.rmtree(space_directory)

    except OSError as error:
        # Prostor je već obrisan iz baze, ali prijavljujemo
        # da datoteke nisu uspješno očišćene.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Prostor je obrisan iz baze, ali direktorij "
                f"sa slikama nije obrisan: {error}"
            ),
        )

    return {
        "message": f"Prostor '{space_name}' je obrisan.",
        "deleted_images_directory": str(space_directory),
    }

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