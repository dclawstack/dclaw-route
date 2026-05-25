import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.core.utils import utc_now


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=False, default="van")
    capacity_kg: Mapped[float] = mapped_column(Float, nullable=False, default=1000.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="available")
    odometer_km: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_service_odometer_km: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_service_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
