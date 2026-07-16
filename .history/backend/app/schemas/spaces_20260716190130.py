from typing import  Dict, List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ==========================================
# KATEGORIJE
# ==========================================

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


# ==========================================
# PODKATEGORIJE
# ==========================================

class SpaceSubcategoryCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    category_id: int = Field(
        gt=0,
    )


class SpaceSubcategoryUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    category_id: Optional[int] = Field(
        default=None,
        gt=0,
    )


class SpaceSubcategoryOut(BaseModel):
    id: int
    name: str
    category_id: int

    category: SpaceCategoryOut

    model_config = ConfigDict(
        from_attributes=True,
    )


# ==========================================
# SLIKE
# ==========================================

class SpaceImageCreate(BaseModel):
    url: str
    is_primary: bool = False


class SpaceImageOut(SpaceImageCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


# ==========================================
# OPREMA
# ==========================================

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


# ==========================================
# DODATNE USLUGE
# ==========================================

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


# ==========================================
# PROSTORI
# ==========================================

class SpaceCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str = Field(
        min_length=1,
    )

    subcategory_id: int = Field(
        gt=0,
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

    images: List[
        SpaceImageCreate
    ] = Field(
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

    subcategory_id: int
    subcategory: SpaceSubcategoryOut

    capacity: int
    price: float
    price_unit: str

    is_modular: bool
    combination_group: Optional[str]

    images: List[
        SpaceImageOut
    ] = Field(
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