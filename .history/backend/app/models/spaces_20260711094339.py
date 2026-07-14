from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    capacity = Column(Integer, nullable=False)
    price_per_hour = Column(Float, nullable=False)
    space_type = Column(String(50), nullable=False)  # ured, konferencijska, vanjski

    images = relationship("SpaceImage", back_populates="space", cascade="all, delete")
    equipment = relationship("SpaceEquipment", back_populates="space", cascade="all, delete")
    services = relationship("SpaceService", back_populates="space", cascade="all, delete")
    reservations = relationship("Reservation", back_populates="space")


class SpaceImage(Base):
    __tablename__ = "space_images"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=False)
    url = Column(String(500), nullable=False)
    is_primary = Column(Integer, default=0)  # 1 = glavna slika

    space = relationship("Space", back_populates="images")


class SpaceEquipment(Base):
    __tablename__ = "space_equipment"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=False)
    name = Column(String(100), nullable=False)  # projektor, mikrofon...

    space = relationship("Space", back_populates="equipment")