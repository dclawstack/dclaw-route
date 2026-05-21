from uuid import UUID
from pydantic import BaseModel


class OptimizeRequest(BaseModel):
    max_stops: int | None = None


class OptimizeResponse(BaseModel):
    route_id: UUID
    original_sequence: list[UUID]
    optimized_sequence: list[UUID]
    original_distance_km: float
    optimized_distance_km: float
    improvement_percent: float
