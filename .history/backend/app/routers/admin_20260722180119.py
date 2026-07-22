from datetime import datetime, timedelta
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

@router.delete(
    "/spaces/{space_id}/images/{image_id}",
    status_code=status.HTTP_200_OK,
)
def delete_space_image(
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

    was_primary = image.is_primary

    # Sigurnije je uzeti samo ime datoteke,
    # a ne direktno vjerovati URL-u iz baze.
    filename = Path(image.url).name
    file_path = (
        UPLOAD_ROOT
        / str(space_id)
        / filename
    )

    try:
        db.delete(image)
        db.flush()

        new_primary = None

        if was_primary:
            new_primary = (
                db.query(SpaceImage)
                .filter(
                    SpaceImage.space_id == space_id,
                    SpaceImage.id != image_id,
                )
                .order_by(SpaceImage.id.asc())
                .first()
            )

            if new_primary:
                new_primary.is_primary = True

        db.commit()

    except Exception:
        db.rollback()
        raise

    # Datoteku brišemo tek nakon uspješnog commita baze.
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            # Zapis je obrisan iz baze, ali datoteka nije.
            # Ovo možeš kasnije zapisivati kroz logger.
            pass

    space_directory = UPLOAD_ROOT / str(space_id)

    # Ako više nema slika, možeš ukloniti prazan direktorij.
    if space_directory.exists():
        try:
            space_directory.rmdir()
        except OSError:
            # Direktorij nije prazan.
            pass

    return {
        "message": "Slika je uspješno obrisana.",
        "new_primary_image": (
            {
                "id": new_primary.id,
                "url": new_primary.url,
                "is_primary": True,
            }
            if new_primary
            else None
        ),
    }
    
@router.get(
    "/spaces/{space_id}/images",
)
def get_space_images(
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

    images = (
        db.query(SpaceImage)
        .filter(SpaceImage.space_id == space_id)
        .order_by(
            SpaceImage.is_primary.desc(),
            SpaceImage.id.asc(),
        )
        .all()
    )

    return [
        {
            "id": image.id,
            "url": image.url,
            "is_primary": image.is_primary,
        }
        for image in images
    ]

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

# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    now = datetime.now()

    today_start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    tomorrow_start = today_start + timedelta(days=1)

    month_start = now.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    if now.month == 12:
        next_month_start = now.replace(
            year=now.year + 1,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
    else:
        next_month_start = now.replace(
            month=now.month + 1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    total_reservations = (
        db.query(func.count(Reservation.id))
        .scalar()
        or 0
    )

    active_spaces = (
        db.query(func.count(Space.id))
        .scalar()
        or 0
    )

    monthly_revenue = (
        db.query(
            func.coalesce(
                func.sum(Reservation.total_price),
                0,
            )
        )
        .filter(
            Reservation.status
            == ReservationStatus.confirmed,
            Reservation.start_time >= month_start,
            Reservation.start_time < next_month_start,
        )
        .scalar()
        or 0
    )

    monthly_reservations = (
        db.query(func.count(Reservation.id))
        .filter(
            Reservation.start_time >= month_start,
            Reservation.start_time < next_month_start,
            Reservation.status
            != ReservationStatus.cancelled,
        )
        .scalar()
        or 0
    )

    today_rows = (
        db.query(Reservation, Space)
        .join(
            Space,
            Space.id == Reservation.space_id,
        )
        .filter(
            Reservation.start_time < tomorrow_start,
            Reservation.end_time > today_start,
            Reservation.status
            != ReservationStatus.cancelled,
        )
        .order_by(Reservation.start_time.asc())
        .all()
    )

    recent_rows = (
        db.query(Reservation, Space)
        .join(
            Space,
            Space.id == Reservation.space_id,
        )
        .order_by(Reservation.id.desc())
        .limit(5)
        .all()
    )

    current_rows = (
        db.query(Reservation, Space)
        .join(
            Space,
            Space.id == Reservation.space_id,
        )
        .filter(
            Reservation.start_time <= now,
            Reservation.end_time > now,
            Reservation.status
            == ReservationStatus.confirmed,
        )
        .all()
    )

    current_reservations_by_space = {
        reservation.space_id: reservation
        for reservation, _space in current_rows
    }

    spaces = (
        db.query(Space)
        .order_by(Space.name.asc())
        .all()
    )

    def get_customer_name(reservation: Reservation) -> str:
        if (
            reservation.company
            and reservation.company.strip()
        ):
            return reservation.company.strip()

        return (
            f"{reservation.first_name} "
            f"{reservation.last_name}"
        ).strip()

    def get_event_name(reservation: Reservation) -> str:
        if reservation.notes and reservation.notes.strip():
            return reservation.notes.strip()

        return "Rezervacija prostora"

    def get_status_value(reservation: Reservation) -> str:
        if hasattr(reservation.status, "value"):
            return reservation.status.value

        return str(reservation.status)

    today_reservations = []

    for reservation, space in today_rows:
        today_reservations.append({
            "id": reservation.id,
            "eventName": get_event_name(reservation),
            "customerName": get_customer_name(
                reservation
            ),
            "spaceId": space.id,
            "spaceName": space.name,
            "startTime": reservation.start_time.strftime(
                "%H:%M"
            ),
            "endTime": reservation.end_time.strftime(
                "%H:%M"
            ),
            "guests": None,
            "status": get_status_value(reservation),
        })

    recent_reservations = []

    for reservation, space in recent_rows:
        recent_reservations.append({
            "id": reservation.id,
            "eventName": get_event_name(reservation),
            "customerName": get_customer_name(
                reservation
            ),
            "spaceId": space.id,
            "spaceName": space.name,
            "date": reservation.start_time.strftime(
                "%d. %m. %Y."
            ),
            "time": (
                f"{reservation.start_time.strftime('%H:%M')}"
                f" – "
                f"{reservation.end_time.strftime('%H:%M')}"
            ),
            "status": get_status_value(reservation),
        })

    space_occupancy = []

    for space in spaces:
        current_reservation = (
            current_reservations_by_space.get(space.id)
        )

        if current_reservation:
            space_occupancy.append({
                "id": space.id,
                "name": space.name,
                "status": "occupied",
                "currentReservationId": (
                    current_reservation.id
                ),
                "currentEvent": get_event_name(
                    current_reservation
                ),
                "occupiedUntil": (
                    current_reservation.end_time
                    .strftime("%H:%M")
                ),
            })
        else:
            space_occupancy.append({
                "id": space.id,
                "name": space.name,
                "status": "available",
                "currentReservationId": None,
                "currentEvent": None,
                "occupiedUntil": None,
            })

    occupied_spaces = sum(
        1
        for space in space_occupancy
        if space["status"] == "occupied"
    )

    available_spaces = sum(
        1
        for space in space_occupancy
        if space["status"] == "available"
    )

    return {
        "statistics": {
            "totalReservations": total_reservations,
            "todayReservations": len(
                today_reservations
            ),
            "activeSpaces": active_spaces,
            "monthlyRevenue": float(
                monthly_revenue
            ),
            "monthlyReservations": (
                monthly_reservations
            ),
            "occupiedSpaces": occupied_spaces,
            "availableSpaces": available_spaces,
        },
        "todayReservations": today_reservations,
        "recentReservations": recent_reservations,
        "spaceOccupancy": space_occupancy,
    }

@router.get("/reports")
def get_admin_reports(
    period: Literal["week", "month", "quarter", "year"] = Query(
        default="year"
    ),
    space_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    now = datetime.now()
    start_date, end_date = get_report_date_range(period, now)

    base_query = db.query(Reservation).filter(
        Reservation.start_time >= start_date,
        Reservation.start_time < end_date,
    )

    if space_id is not None:
        base_query = base_query.filter(
            Reservation.space_id == space_id
        )

    reservations = base_query.all()

    total_reservations = len(reservations)

    cancelled_reservations = sum(
        1
        for reservation in reservations
        if get_status_value(reservation.status) == "cancelled"
    )

    revenue_reservations = [
        reservation
        for reservation in reservations
        if get_status_value(reservation.status)
        in {"confirmed", "completed"}
    ]

    total_revenue = sum(
        float(reservation.total_price or 0)
        for reservation in revenue_reservations
    )

    average_reservation_value = (
        total_revenue / len(revenue_reservations)
        if revenue_reservations
        else 0
    )

    monthly_data = build_monthly_data(
        reservations=reservations,
        start_date=start_date,
        end_date=end_date,
    )

    space_performance = build_space_performance(
        db=db,
        reservations=reservations,
        selected_space_id=space_id,
    )

    reservation_statuses = build_reservation_statuses(
        reservations
    )

    spaces_query = db.query(Space).order_by(Space.name.asc())

    if space_id is not None:
        spaces_query = spaces_query.filter(
            Space.id == space_id
        )

    spaces = spaces_query.all()

    return {
        "filters": {
            "period": period,
            "spaceId": space_id,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        },
        "spaces": [
            {
                "id": space.id,
                "name": space.name,
            }
            for space in spaces
        ],
        "statistics": {
            "totalReservations": total_reservations,
            "totalRevenue": round(total_revenue, 2),
            "averageReservationValue": round(
                average_reservation_value,
                2,
            ),
            "cancelledReservations": cancelled_reservations,
        },
        "monthlyData": monthly_data,
        "spacePerformance": space_performance,
        "reservationStatuses": reservation_statuses,
    }

def get_report_date_range(
    period: str,
    now: datetime,
) -> tuple[datetime, datetime]:
    if period == "week":
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        end_date = start_date + timedelta(days=7)

        return start_date, end_date

    if period == "month":
        start_date = now.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        if start_date.month == 12:
            end_date = start_date.replace(
                year=start_date.year + 1,
                month=1,
            )
        else:
            end_date = start_date.replace(
                month=start_date.month + 1,
            )

        return start_date, end_date

    if period == "quarter":
        quarter_start_month = (
            ((now.month - 1) // 3) * 3
        ) + 1

        start_date = now.replace(
            month=quarter_start_month,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        next_quarter_month = quarter_start_month + 3

        if next_quarter_month > 12:
            end_date = start_date.replace(
                year=start_date.year + 1,
                month=next_quarter_month - 12,
            )
        else:
            end_date = start_date.replace(
                month=next_quarter_month,
            )

        return start_date, end_date

    start_date = now.replace(
        month=1,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    end_date = start_date.replace(
        year=start_date.year + 1,
    )

    return start_date, end_date
    
def get_status_value(status) -> str:
    if hasattr(status, "value"):
        return status.value

    return str(status)

MONTH_NAMES = {
    1: {
        "short": "Sij",
        "full": "Siječanj",
    },
    2: {
        "short": "Velj",
        "full": "Veljača",
    },
    3: {
        "short": "Ožu",
        "full": "Ožujak",
    },
    4: {
        "short": "Tra",
        "full": "Travanj",
    },
    5: {
        "short": "Svi",
        "full": "Svibanj",
    },
    6: {
        "short": "Lip",
        "full": "Lipanj",
    },
    7: {
        "short": "Srp",
        "full": "Srpanj",
    },
    8: {
        "short": "Kol",
        "full": "Kolovoz",
    },
    9: {
        "short": "Ruj",
        "full": "Rujan",
    },
    10: {
        "short": "Lis",
        "full": "Listopad",
    },
    11: {
        "short": "Stu",
        "full": "Studeni",
    },
    12: {
        "short": "Pro",
        "full": "Prosinac",
    },
}

def build_monthly_data(
    reservations: list[Reservation],
    start_date: datetime,
    end_date: datetime,
) -> list[dict]:
    monthly_values = {}

    current_month = start_date.replace(day=1)

    while current_month < end_date:
        key = (
            current_month.year,
            current_month.month,
        )

        monthly_values[key] = {
            "month": MONTH_NAMES[current_month.month][
                "short"
            ],
            "fullMonth": (
                f"{MONTH_NAMES[current_month.month]['full']} "
                f"{current_month.year}"
            ),
            "reservations": 0,
            "revenue": 0,
        }

        if current_month.month == 12:
            current_month = current_month.replace(
                year=current_month.year + 1,
                month=1,
            )
        else:
            current_month = current_month.replace(
                month=current_month.month + 1,
            )

    for reservation in reservations:
        key = (
            reservation.start_time.year,
            reservation.start_time.month,
        )

        if key not in monthly_values:
            continue

        monthly_values[key]["reservations"] += 1

        if get_status_value(reservation.status) in {
            "confirmed",
            "completed",
        }:
            monthly_values[key]["revenue"] += float(
                reservation.total_price or 0
            )

    result = list(monthly_values.values())

    for item in result:
        item["revenue"] = round(
            item["revenue"],
            2,
        )

    return result

def build_space_performance(
    db: Session,
    reservations: list[Reservation],
    selected_space_id: Optional[int] = None,
) -> list[dict]:
    spaces_query = db.query(Space)

    if selected_space_id is not None:
        spaces_query = spaces_query.filter(
            Space.id == selected_space_id
        )

    spaces = spaces_query.order_by(
        Space.name.asc()
    ).all()

    reservations_by_space = {}

    for reservation in reservations:
        reservations_by_space.setdefault(
            reservation.space_id,
            [],
        ).append(reservation)

    result = []

    for space in spaces:
        space_reservations = reservations_by_space.get(
            space.id,
            [],
        )

        revenue = sum(
            float(reservation.total_price or 0)
            for reservation in space_reservations
            if get_status_value(reservation.status)
            in {"confirmed", "completed"}
        )

        cancelled = sum(
            1
            for reservation in space_reservations
            if get_status_value(reservation.status)
            == "cancelled"
        )

        result.append({
            "id": space.id,
            "name": space.name,
            "reservations": len(space_reservations),
            "revenue": round(revenue, 2),
            "cancelledReservations": cancelled,
        })

    result.sort(
        key=lambda item: item["reservations"],
        reverse=True,
    )

    return result

def build_reservation_statuses(
    reservations: list[Reservation],
) -> list[dict]:
    status_labels = {
        "pending": "Na čekanju",
        "confirmed": "Potvrđene",
        "completed": "Završene",
        "cancelled": "Otkazane",
    }

    counts = {
        "pending": 0,
        "confirmed": 0,
        "completed": 0,
        "cancelled": 0,
    }

    for reservation in reservations:
        status = get_status_value(
            reservation.status
        )

        if status in counts:
            counts[status] += 1

    total = len(reservations)

    result = []

    for status, label in status_labels.items():
        count = counts[status]

        percentage = (
            round((count / total) * 100, 1)
            if total
            else 0
        )

        result.append({
            "status": status,
            "label": label,
            "count": count,
            "percentage": percentage,
        })

    return result