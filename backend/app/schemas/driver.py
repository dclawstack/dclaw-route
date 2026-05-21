from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DriverBase(BaseModel):
    name: str
    email: str
    phone: str | None = None
    vehicle_type: str = "van"
    status: str = "active"


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    vehicle_type: str | None = None
    status: str | None = None


class DriverRead(DriverBase):
    id: UUID
    current_lat: float | None = None
    current_lng: float | None = None
    location_updated_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
