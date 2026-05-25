from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.schemas.delivery import DeliveryRead


class RouteBase(BaseModel):
    name: str
    driver_id: UUID | None = None
    vehicle_id: UUID | None = None
    status: str = "planned"
    total_distance_km: float = 0.0
    estimated_minutes: int = 0


class RouteCreate(RouteBase):
    stop_ids: list[UUID] = []


class RouteUpdate(BaseModel):
    name: str | None = None
    driver_id: UUID | None = None
    vehicle_id: UUID | None = None
    status: str | None = None
    total_distance_km: float | None = None
    estimated_minutes: int | None = None


class RouteRead(RouteBase):
    id: UUID
    created_at: datetime
    deliveries: list[DeliveryRead] = []

    model_config = ConfigDict(from_attributes=True)
