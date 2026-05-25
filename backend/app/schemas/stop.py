from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class StopBase(BaseModel):
    name: str
    address: str
    lat: float
    lng: float
    notes: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None


class StopCreate(StopBase):
    pass


class StopUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    notes: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None


class StopRead(StopBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
