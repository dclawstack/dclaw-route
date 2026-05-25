from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DeliveryBase(BaseModel):
    route_id: UUID
    stop_id: UUID
    sequence: int = 0
    kind: str = "drop_off"
    status: str = "pending"
    notes: str | None = None


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(BaseModel):
    sequence: int | None = None
    status: str | None = None
    notes: str | None = None
    completed_at: datetime | None = None


class DeliveryRead(DeliveryBase):
    id: UUID
    completed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
