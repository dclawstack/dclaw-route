from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DeliveryProofSubmit(BaseModel):
    photo_b64: str | None = None
    signature_b64: str | None = None
    barcode: str | None = None
    geotag_lat: float | None = None
    geotag_lng: float | None = None
    notes: str | None = None


class DeliveryProofRead(BaseModel):
    id: UUID
    status: str
    photo_b64: str | None
    signature_b64: str | None
    barcode: str | None
    geotag_lat: float | None
    geotag_lng: float | None
    photo_validated: bool | None
    notes: str | None
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
