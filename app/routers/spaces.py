from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.spaces import Space, SpaceImage, SpaceEquipment
from app.schemas.spaces import SpaceCreate, SpaceOut

router = APIRouter(prefix="/spaces", tags=["Prostori"])

@router.post("/", response_model=SpaceOut)
def create_space(space: SpaceCreate, db: Session = Depends(get_db)):
    db_space = Space(
        name=space.name,
        description=space.description,
        capacity=space.capacity,
        price_per_hour=space.price_per_hour,
        space_type=space.space_type,
    )
    db.add(db_space)
    db.flush()  # da dobijemo id prije commitanja

    for img in space.images:
        db.add(SpaceImage(space_id=db_space.id, url=img.url, is_primary=img.is_primary))

    for eq in space.equipment:
        db.add(SpaceEquipment(space_id=db_space.id, name=eq.name))

    db.commit()
    db.refresh(db_space)
    return db_space