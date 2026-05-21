from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class LocationPing(BaseModel):
    lat: float
    lng: float


class DriverLocation(BaseModel):
    driver_id: UUID
    current_lat: float | None
    current_lng: float | None
    location_updated_at: datetime | None


class StopETARead(BaseModel):
    delivery_id: UUID
    stop_id: UUID
    stop_name: str
    sequence: int
    distance_from_previous_km: float
    cumulative_km: float
    eta: datetime
    minutes_from_now: int


class RouteETARead(BaseModel):
    route_id: UUID
    driver_id: UUID | None
    driver_position: tuple[float, float] | None
    stops: list[StopETARead]
    is_delayed: bool
