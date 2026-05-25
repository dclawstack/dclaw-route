from uuid import UUID
from pydantic import BaseModel


class InsertUrgentRequest(BaseModel):
    stop_id: UUID


class StopImpactRead(BaseModel):
    delivery_id: UUID
    stop_name: str
    old_sequence: int
    new_sequence: int
    eta_shift_minutes: int


class InsertResultRead(BaseModel):
    route_id: UUID
    inserted_delivery_id: UUID
    inserted_at_position: int
    extra_distance_km: float
    extra_minutes: int
    shifted_stops: list[StopImpactRead]
