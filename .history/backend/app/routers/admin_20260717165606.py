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
    SpaceCategory,
    SpaceEquipment,
    SpaceImage,
    SpaceSubcategory,
)
from app.models.users import User
from app.models.spaces import (
    Space,
    SpaceCategory,
    SpaceEquipment,
    SpaceImage,
    SpaceSubcategory,
)
from app.schemas.spaces import (
    SpaceCategoryCreate,
    SpaceCategoryOut,
    SpaceCategoryUpdate,
    SpaceCreate,
    SpaceOut,
    SpaceSubcategoryCreate,
    SpaceSubcategoryOut,
    SpaceSubcategoryUpdate,
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

ALLOWED_WORKING_DAYS = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}


def prepare_working_hours(working_hours):
    normalized_hours = {}

    for day, schedule in working_hours.items():
        if day not in ALLOWED_WORKING_DAYS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Neispravan dan u radnom vremenu: {day}.",
            )

        if schedule.is_closed:
            normalized_hours[day] = {
                "is_closed": True,
                "opens_at": None,
                "closes_at": None,
            }
            continue

        if not schedule.opens_at or not schedule.closes_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Vrijeme otvaranja i zatvaranja "
                    f"obavezno je za dan '{day}'."
                ),
            )

        if schedule.opens_at >= schedule.closes_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Vrijeme otvaranja mora biti prije "
                    f"zatvaranja za dan '{day}'."
                ),
            )

        normalized_hours[day] = {
            "is_closed": False,
            "opens_at": schedule.opens_at,
            "closes_at": schedule.closes_at,
        }

    return normalized_hours


# ─── KATEGORIJE PROSTORA ──────────────────────────────────────────────────────


@router.get(
    "/space-categories",
    response_model=List[SpaceCategoryOut],
)
def get_space_categories(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return (
        db.query(SpaceCategory)
        .order_by(SpaceCategory.name.asc())
        .all()
    )


@router.get(
    "/space-categories/{category_id}",
    response_model=SpaceCategoryOut,
)
def get_space_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    category = (
        db.query(SpaceCategory)
        .filter(SpaceCategory.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategorija nije pronađena.",
        )

    return category


@router.post(
    "/space-categories",
    response_model=SpaceCategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_space_category(
    data: SpaceCategoryCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    normalized_name = data.name.strip()

    existing_category = (
        db.query(SpaceCategory)
        .filter(
            func.lower(SpaceCategory.name)
            == normalized_name.lower()
        )
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kategorija s tim nazivom već postoji.",
        )

    category = SpaceCategory(
        name=normalized_name,
    )

    try:
        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kategorija s tim nazivom već postoji.",
        )


@router.put(
    "/space-categories/{category_id}",
    response_model=SpaceCategoryOut,
)
def update_space_category(
    category_id: int,
    data: SpaceCategoryUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    category = (
        db.query(SpaceCategory)
        .filter(SpaceCategory.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategorija nije pronađena.",
        )

    normalized_name = data.name.strip()

    duplicate_category = (
        db.query(SpaceCategory)
        .filter(
            func.lower(SpaceCategory.name)
            == normalized_name.lower(),
            SpaceCategory.id != category_id,
        )
        .first()
    )

    if duplicate_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kategorija s tim nazivom već postoji.",
        )

    try:
        category.name = normalized_name

        db.commit()
        db.refresh(category)

        return category

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kategorija s tim nazivom već postoji.",
        )


@router.delete(
    "/space-categories/{category_id}",
)
def delete_space_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    category = (
        db.query(SpaceCategory)
        .filter(SpaceCategory.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategorija nije pronađena.",
        )

    existing_subcategory = (
        db.query(SpaceSubcategory)
        .filter(
            SpaceSubcategory.category_id == category_id
        )
        .first()
    )

    if existing_subcategory:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Kategoriju nije moguće obrisati jer "
                "sadrži podkategorije."
            ),
        )

    category_name = category.name

    try:
        db.delete(category)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kategoriju trenutno nije moguće obrisati.",
        )

    return {
        "message": (
            f"Kategorija '{category_name}' je obrisana."
        ),
    }

# ─── PODKATEGORIJE PROSTORA ───────────────────────────────────────────────────


@router.get(
    "/space-subcategories",
    response_model=List[SpaceSubcategoryOut],
)
def get_space_subcategories(
    category_id: Optional[int] = Query(
        default=None,
        gt=0,
        description="Filtriranje podkategorija po kategoriji",
    ),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    query = db.query(SpaceSubcategory)

    if category_id is not None:
        query = query.filter(
            SpaceSubcategory.category_id == category_id
        )

    return (
        query
        .order_by(SpaceSubcategory.name.asc())
        .all()
    )


@router.get(
    "/space-subcategories/{subcategory_id}",
    response_model=SpaceSubcategoryOut,
)
def get_space_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    subcategory = (
        db.query(SpaceSubcategory)
        .filter(
            SpaceSubcategory.id == subcategory_id
        )
        .first()
    )

    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podkategorija nije pronađena.",
        )

    return subcategory


@router.post(
    "/space-subcategories",
    response_model=SpaceSubcategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_space_subcategory(
    data: SpaceSubcategoryCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    category = (
        db.query(SpaceCategory)
        .filter(
            SpaceCategory.id == data.category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategorija nije pronađena.",
        )

    normalized_name = data.name.strip()

    existing_subcategory = (
        db.query(SpaceSubcategory)
        .filter(
            SpaceSubcategory.category_id
            == data.category_id,
            func.lower(SpaceSubcategory.name)
            == normalized_name.lower(),
        )
        .first()
    )

    if existing_subcategory:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Podkategorija s tim nazivom već postoji "
                "u odabranoj kategoriji."
            ),
        )

    subcategory = SpaceSubcategory(
        name=normalized_name,
        category_id=data.category_id,
    )

    try:
        db.add(subcategory)
        db.commit()
        db.refresh(subcategory)

        return subcategory

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Podkategorija s tim nazivom već postoji "
                "u odabranoj kategoriji."
            ),
        )


@router.put(
    "/space-subcategories/{subcategory_id}",
    response_model=SpaceSubcategoryOut,
)
def update_space_subcategory(
    subcategory_id: int,
    data: SpaceSubcategoryUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    subcategory = (
        db.query(SpaceSubcategory)
        .filter(
            SpaceSubcategory.id == subcategory_id
        )
        .first()
    )

    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podkategorija nije pronađena.",
        )

    target_category_id = (
        data.category_id
        if data.category_id is not None
        else subcategory.category_id
    )

    category = (
        db.query(SpaceCategory)
        .filter(
            SpaceCategory.id == target_category_id
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategorija nije pronađena.",
        )

    target_name = (
        data.name.strip()
        if data.name is not None
        else subcategory.name
    )

    duplicate_subcategory = (
        db.query(SpaceSubcategory)
        .filter(
            SpaceSubcategory.category_id
            == target_category_id,
            func.lower(SpaceSubcategory.name)
            == target_name.lower(),
            SpaceSubcategory.id != subcategory_id,
        )
        .first()
    )

    if duplicate_subcategory:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Podkategorija s tim nazivom već postoji "
                "u odabranoj kategoriji."
            ),
        )

    try:
        subcategory.name = target_name
        subcategory.category_id = target_category_id

        db.commit()
        db.refresh(subcategory)

        return subcategory

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Podkategorija s tim nazivom već postoji "
                "u odabranoj kategoriji."
            ),
        )


@router.delete(
    "/space-subcategories/{subcategory_id}",
)
def delete_space_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    subcategory = (
        db.query(SpaceSubcategory)
        .filter(
            SpaceSubcategory.id == subcategory_id
        )
        .first()
    )

    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podkategorija nije pronađena.",
        )

    existing_space = (
        db.query(Space)
        .filter(
            Space.subcategory_id == subcategory_id
        )
        .first()
    )

    if existing_space:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Podkategoriju nije moguće obrisati jer "
                "je koristi barem jedan prostor."
            ),
        )

    subcategory_name = subcategory.name

    try:
        db.delete(subcategory)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Podkategoriju trenutno nije moguće obrisati.",
        )

    return {
        "message": (
            f"Podkategorija '{subcategory_name}' je obrisana."
        ),
    }

@router.post(
    "/spaces/{space_id}/images",
    status_code=status.HTTP_201_CREATED,
)
async def upload_space_images(
    space_id: int,
    images: Annotated[
        list[UploadFile],
        File(
            description="JPG, PNG ili WEBP slike prostora",
        ),
    ],
    primary_index: int | None = None,
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

    existing_images_count = (
        db.query(SpaceImage)
        .filter(SpaceImage.space_id == space_id)
        .count()
    )

    if existing_images_count + len(images) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Prostor može imati najviše 10 slika. "
                f"Trenutno ima {existing_images_count}, "
                f"a pokušavate dodati {len(images)}."
            ),
        )

    if primary_index is not None:
        if primary_index < 0 or primary_index >= len(images):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Neispravan indeks glavne slike.",
            )

    existing_primary = (
        db.query(SpaceImage)
        .filter(
            SpaceImage.space_id == space_id,
            SpaceImage.is_primary.is_(True),
        )
        .first()
    )

    effective_primary_index = primary_index

    # Ako prostor još nema glavnu sliku,
    # prva nova slika automatski postaje glavna.
    if existing_primary is None and primary_index is None:
        effective_primary_index = 0

    space_directory = UPLOAD_ROOT / str(space_id)
    space_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    saved_paths: list[Path] = []
    created_images: list[SpaceImage] = []

    try:
        # Staru glavnu sliku skidamo samo ako je admin
        # izričito odabrao jednu od novih kao glavnu.
        if primary_index is not None:
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
                space_directory
                / generated_filename
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
                is_primary=(
                    effective_primary_index is not None
                    and index == effective_primary_index
                ),
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
            
            
@router.patch(
    "/spaces/{space_id}/images/{image_id}/primary",
)
def set_primary_space_image(
    space_id: int,
    image_id: int,
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

    image = (
        db.query(SpaceImage)
        .filter(
            SpaceImage.id == image_id,
            SpaceImage.space_id == space_id,
        )
        .first()
    )

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slika nije pronađena za odabrani prostor.",
        )

    if image.is_primary:
        return {
            "message": "Odabrana slika je već glavna.",
            "image": {
                "id": image.id,
                "url": image.url,
                "is_primary": image.is_primary,
            },
        }

    try:
        db.query(SpaceImage).filter(
            SpaceImage.space_id == space_id,
            SpaceImage.is_primary.is_(True),
        ).update(
            {"is_primary": False},
            synchronize_session=False,
        )

        image.is_primary = True

        db.commit()
        db.refresh(image)

        return {
            "message": "Glavna slika je uspješno promijenjena.",
            "image": {
                "id": image.id,
                "url": image.url,
                "is_primary": image.is_primary,
            },
        }

    except Exception:
        db.rollback()
        raise



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

    subcategory = (
        db.query(SpaceSubcategory)
        .filter(
            SpaceSubcategory.id
            == data.subcategory_id
        )
        .first()
    )

    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podkategorija nije pronađena.",
        )

    working_hours = prepare_working_hours(
        data.working_hours
    )

    space = Space(
        name=data.name.strip(),
        description=data.description.strip(),
        subcategory_id=data.subcategory_id,
        capacity=data.capacity,
        price=data.price,
        price_unit=data.price_unit,
        is_modular=data.is_modular,
        combination_group=(
            data.combination_group.strip()
            if (
                data.is_modular
                and data.combination_group
            )
            else None
        ),
        working_hours=working_hours,
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
                    name=equipment.name.strip(),
                )
            )

        for service in data.services:
            db.add(
                SpaceService(
                    space_id=space.id,
                    name=service.name.strip(),
                    description=service.description,
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
        description="Pretraga po nazivu i opisu prostora",
    ),
    category_id: Optional[int] = Query(
        default=None,
        gt=0,
        description="Filtriranje po kategoriji",
    ),
    subcategory_id: Optional[int] = Query(
        default=None,
        gt=0,
        description="Filtriranje po podkategoriji",
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

    query = db.query(Space)

    if search:
        search_value = search.strip()

        if search_value:
            search_pattern = f"%{search_value}%"

            query = query.filter(
                or_(
                    Space.name.ilike(search_pattern),
                    Space.description.ilike(search_pattern),
                )
            )

    if subcategory_id is not None:
        query = query.filter(
            Space.subcategory_id == subcategory_id
        )

    if category_id is not None:
        query = (
            query.join(Space.subcategory)
            .filter(
                SpaceSubcategory.category_id
                == category_id
            )
        )

    if min_capacity is not None:
        query = query.filter(
            Space.capacity >= min_capacity
        )

    if max_capacity is not None:
        query = query.filter(
            Space.capacity <= max_capacity
        )

    if is_modular is not None:
        query = query.filter(
            Space.is_modular == is_modular
        )

    return (
        query
        .order_by(Space.name.asc())
        .all()
    )


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

    subcategory = (
        db.query(SpaceSubcategory)
        .filter(
            SpaceSubcategory.id
            == data.subcategory_id
        )
        .first()
    )

    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Podkategorija nije pronađena.",
        )

    duplicate_space = (
        db.query(Space)
        .filter(
            func.lower(Space.name)
            == data.name.strip().lower(),
            Space.id != space_id,
        )
        .first()
    )

    if duplicate_space:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Prostor s tim nazivom već postoji.",
        )

    working_hours = prepare_working_hours(
        data.working_hours
    )

    try:
        space.name = data.name.strip()
        space.description = data.description.strip()
        space.subcategory_id = data.subcategory_id

        space.capacity = data.capacity
        space.price = data.price
        space.price_unit = data.price_unit

        space.is_modular = data.is_modular
        space.combination_group = (
            data.combination_group.strip()
            if (
                data.is_modular
                and data.combination_group
            )
            else None
        )

        space.working_hours = working_hours

        db.query(SpaceEquipment).filter(
            SpaceEquipment.space_id == space_id
        ).delete(
            synchronize_session=False
        )

        db.query(SpaceService).filter(
            SpaceService.space_id == space_id
        ).delete(
            synchronize_session=False
        )

        for equipment in data.equipment:
            db.add(
                SpaceEquipment(
                    space_id=space_id,
                    name=equipment.name.strip(),
                )
            )

        for service in data.services:
            db.add(
                SpaceService(
                    space_id=space_id,
                    name=service.name.strip(),
                    description=service.description,
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