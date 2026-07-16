from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


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

    # Kategorizacija
    space_type = Column(
        String(50),
        nullable=False,
    )

    space_subtype = Column(
        String(50),
        nullable=False,
    )

    capacity = Column(
        Integer,
        nullable=False,
    )

    # Naplata
    price = Column(
        Float,
        nullable=False,
    )

    price_unit = Column(
        String(30),
        nullable=False,
        default="hour",
    )

    # Modularne/povezive konferencijske dvorane
    is_modular = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    combination_group = Column(
        String(50),
        nullable=True,
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
        ForeignKey("spaces.id"),
        nullable=False,
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
        ForeignKey("spaces.id"),
        nullable=False,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    space = relationship(
        "Space",
        back_populates="equipment",
    )
