from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class RecurringType(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"

class ReservationStatus(str, enum.Enum):
    pending = "pending"       # čeka potvrdu
    confirmed = "confirmed"   # potvrđena
    cancelled = "cancelled"   # otkazana

class SpaceService(Base):
    __tablename__ = "space_services"

    id = Column(Integer, primary_key=True, index=True)

    space_id = Column(
        Integer,
        ForeignKey("spaces.id"),
        nullable=False,
    )

    name = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)

    description = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)

    price = Column(Float, nullable=False, default=0)
    conditions = Column(Text, nullable=True)

    space = relationship(
        "Space",
        back_populates="services",
    )

    reservation_services = relationship(
        "ReservationService",
        back_populates="service",
    )

class RecurringRule(Base):
    __tablename__ = "recurring_rules"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(RecurringType), nullable=False)   # daily / weekly
    interval = Column(Integer, default=1)                # svaki 1 dan/tjedan
    end_date = Column(DateTime, nullable=False)          # do kada se ponavlja

    reservations = relationship("Reservation", back_populates="recurring_rule")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=False)
    recurring_rule_id = Column(Integer, ForeignKey("recurring_rules.id"), nullable=True)

    # Podaci korisnika
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=False)
    company = Column(String(200), nullable=True)

    # Termin
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Cijene
    total_price = Column(Float, nullable=False)

    # Status i Google Calendar
    status = Column(Enum(ReservationStatus), default=ReservationStatus.pending)
    google_event_id = Column(String(200), nullable=True)  # ID eventa u Google kalendaru
    notes = Column(Text, nullable=True)

    space = relationship("Space", back_populates="reservations")
    recurring_rule = relationship("RecurringRule", back_populates="reservations")
    services = relationship("ReservationService", back_populates="reservation", cascade="all, delete")


class ReservationService(Base):
    __tablename__ = "reservation_services"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("space_services.id"), nullable=False)
    price_at_booking = Column(Float, nullable=False)  # cijena u trenutku rezervacije

    reservation = relationship("Reservation", back_populates="services")
    service = relationship("SpaceService", back_populates="reservation_services")