from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TerritoryBase(BaseModel):
    name: str
    color: str = "#10B981"


class TerritoryCreate(TerritoryBase):
    pass


class TerritoryUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class TerritoryRead(TerritoryBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClusterRequest(BaseModel):
    n: int = 3  # number of territories
    max_iterations: int = 20


class TerritoryAssignment(BaseModel):
    territory_id: UUID
    name: str
    color: str
    stop_count: int
    center_lat: float
    center_lng: float


class ClusterResult(BaseModel):
    territories: list[TerritoryAssignment]
    assigned_stops: int
    iterations: int
