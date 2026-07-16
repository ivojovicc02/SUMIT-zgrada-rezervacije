from typing import List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class SpaceCategoryCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )


class SpaceCategoryUpdate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )


class SpaceCategoryOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class SpaceImageCreate(BaseModel):
    url: str
    is_primary: bool = False


class SpaceImageOut(SpaceImageCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class SpaceEquipmentCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )


class SpaceEquipmentOut(
    SpaceEquipmentCreate
):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class SpaceServiceCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: Optional[str] = None

    price: float = Field(
        default=0,
        ge=0,
    )

    conditions: Optional[str] = None


class SpaceServiceOut(
    SpaceServiceCreate
):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class SpaceCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str = Field(
        min_length=1,
    )

    category_id: int = Field(
        gt=0,
    )

    space_subtype: str = Field(
        min_length=1,
        max_length=100,
    )

    capacity: int = Field(
        ge=1,
    )

    price: float = Field(
        ge=0,
    )

    price_unit: str = Field(
        min_length=1,
        max_length=30,
    )

    is_modular: bool = False

    combination_group: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    images: List[SpaceImageCreate] = Field(
        default_factory=list,
    )

    equipment: List[
        SpaceEquipmentCreate
    ] = Field(
        default_factory=list,
    )

    services: List[
        SpaceServiceCreate
    ] = Field(
        default_factory=list,
    )


class SpaceOut(BaseModel):
    id: int

    name: str
    description: str

    category_id: int
    category: SpaceCategoryOut

    space_subtype: str

    capacity: int
    price: float
    price_unit: str

    is_modular: bool
    combination_group: Optional[str]

    images: List[SpaceImageOut] = Field(
        default_factory=list,
    )

    equipment: List[
        SpaceEquipmentOut
    ] = Field(
        default_factory=list,
    )

    services: List[
        SpaceServiceOut
    ] = Field(
        default_factory=list,
    )

    model_config = ConfigDict(
        from_attributes=True,
    )