from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class SpaceCategory(Base):
    __tablename__ = "space_categories"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True,
    )

    subcategories = relationship(
        "SpaceSubcategory",
        back_populates="category",
    )


class SpaceSubcategory(Base):
    __tablename__ = "space_subcategories"

    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "name",
            name="uq_space_subcategory_category_name",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    category_id = Column(
        Integer,
        ForeignKey(
            "space_categories.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    category = relationship(
        "SpaceCategory",
        back_populates="subcategories",
    )

    spaces = relationship(
        "Space",
        back_populates="subcategory",
    )


class Space(Base):
    __tablename__ = "spaces"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    subcategory_id = Column(
        Integer,
        ForeignKey(
            "space_subcategories.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    capacity = Column(
        Integer,
        nullable=False,
    )

    price = Column(
        Float,
        nullable=False,
    )

    price_unit = Column(
        String(30),
        nullable=False,
        default="hour",
    )

    is_modular = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    combination_group = Column(
        String(50),
        nullable=True,
    )
    
    working_hours = Column(
        JSON,
        nullable=False,
        default=dict,
   ) 

    subcategory = relationship(
        "SpaceSubcategory",
        back_populates="spaces",
    )

    images = relationship(
        "SpaceImage",
        back_populates="space",
        cascade="all, delete-orphan",
    )

    equipment = relationship(
        "SpaceEquipment",
        back_populates="space",
        cascade="all, delete-orphan",
    )

    services = relationship(
        "SpaceService",
        back_populates="space",
        cascade="all, delete-orphan",
    )

    reservations = relationship(
        "Reservation",
        back_populates="space",
    )


class SpaceImage(Base):
    __tablename__ = "space_images"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    space_id = Column(
        Integer,
        ForeignKey(
            "spaces.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    url = Column(
        String(500),
        nullable=False,
    )

    is_primary = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    space = relationship(
        "Space",
        back_populates="images",
    )


class SpaceEquipment(Base):
    __tablename__ = "space_equipment"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    space_id = Column(
        Integer,
        ForeignKey(
            "spaces.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    space = relationship(
        "Space",
        back_populates="equipment",
    )