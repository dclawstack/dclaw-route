from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class GigDriverBase(BaseModel):
    name: str
    phone: str | None = None
    rating: float = 5.0
    vehicle_type: str = "car"
    current_lat: float | None = None
    current_lng: float | None = None
    status: str = "available"


class GigDriverCreate(GigDriverBase):
    pass


class GigDriverUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    rating: float | None = None
    vehicle_type: str | None = None
    current_lat: float | None = None
    current_lng: float | None = None
    status: str | None = None


class GigDriverRead(GigDriverBase):
    id: UUID
    current_route_id: UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GigRequest(BaseModel):
    route_id: UUID
    vehicle_type: str | None = None
    min_rating: float = 3.0
    near_lat: float | None = None
    near_lng: float | None = None


class GigAssignment(BaseModel):
    gig_driver_id: UUID
    gig_driver_name: str
    rating: float
    vehicle_type: str
    distance_km: float | None
    route_id: UUID
