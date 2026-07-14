from fastapi import APIRouter, Depends, HTTPException ,status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.spaces import Space, SpaceImage, SpaceEquipment
from app.schemas.spaces import SpaceCreate, SpaceOut
from app.services.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
    get_current_admin,
)

router = APIRouter(prefix="/spaces", tags=["Prostori"])

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
    validate_space_data(data)

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