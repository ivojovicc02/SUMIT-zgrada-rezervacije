from pydantic import BaseModel
from typing import List, Optional

class SpaceImageIn(BaseModel):
    url: str
    is_primary: int = 0

class SpaceEquipmentIn(BaseModel):
    name: str

class SpaceCreate(BaseModel):
    name: str
    description: str
    capacity: int
    price_per_hour: float
    space_type: str
    images: List[SpaceImageIn] = []
    equipment: List[SpaceEquipmentIn] = []

class SpaceOut(SpaceCreate):
    id: int
    images: List[SpaceImageIn]
    equipment: List[SpaceEquipmentIn]

    class Config:
        from_attributes = True