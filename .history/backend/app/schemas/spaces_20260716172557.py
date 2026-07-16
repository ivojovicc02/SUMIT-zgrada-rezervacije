from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SpaceImageCreate(BaseModel):
    url: str
    is_primary: bool = False


class SpaceImageOut(SpaceImageCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SpaceEquipmentCreate(BaseModel):
    name: str


class SpaceEquipmentOut(SpaceEquipmentCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SpaceServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(default=0, ge=0)
    conditions: Optional[str] = None


class SpaceServiceOut(SpaceServiceCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SpaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)

    space_type: str
    space_subtype: str

    capacity: int = Field(ge=1)
    price: float = Field(ge=0)
    price_unit: str

    is_modular: bool = False
    combination_group: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    images: List[SpaceImageCreate] = []
    equipment: List[SpaceEquipmentCreate] = []
    services: List[SpaceServiceCreate] = []


class SpaceOut(BaseModel):
    id: int

    name: str
    description: str
    
    space_type: str
    space_subtype: str

    capacity: int
    price: float
    price_unit: str

    is_modular: bool
    combination_group: Optional[str]

    images: List[SpaceImageOut]
    equipment: List[SpaceEquipmentOut]
    services: List[SpaceServiceOut]

    model_config = ConfigDict(from_attributes=True)