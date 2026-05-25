from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AvBase(BaseModel):
    vendor: str
    model: str
    autopilot_level: int = 4
    capacity_kg: float = 500.0
    current_lat: float | None = None
    current_lng: float | None = None
    status: str = "available"


class AvCreate(AvBase):
    pass


class AvUpdate(BaseModel):
    vendor: str | None = None
    model: str | None = None
    autopilot_level: int | None = None
    capacity_kg: float | None = None
    current_lat: float | None = None
    current_lng: float | None = None
    status: str | None = None


class AvRead(AvBase):
    id: UUID
    current_route_id: UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DispatchRequest(BaseModel):
    route_id: UUID
    min_autopilot_level: int = 4


class DispatchResult(BaseModel):
    av_id: UUID
    vendor: str
    model: str
    autopilot_level: int
    route_id: UUID
