from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ReturnRequestPayload(BaseModel):
    stop_id: UUID
    notes: str | None = None


class ReturnPickupRead(BaseModel):
    id: UUID
    route_id: UUID
    stop_id: UUID
    sequence: int
    kind: str
    status: str
    notes: str | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConsolidationResult(BaseModel):
    route_id: UUID
    route_name: str
    consolidated_count: int
    total_distance_km: float
    estimated_minutes: int
