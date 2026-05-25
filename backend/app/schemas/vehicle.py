from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class VehicleBase(BaseModel):
    plate: str
    vehicle_type: str = "van"
    capacity_kg: float = 1000.0
    status: str = "available"
    odometer_km: int = 0
    last_service_odometer_km: int = 0


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    plate: str | None = None
    vehicle_type: str | None = None
    capacity_kg: float | None = None
    status: str | None = None
    odometer_km: int | None = None
    last_service_odometer_km: int | None = None
    last_service_at: datetime | None = None


class VehicleRead(VehicleBase):
    id: UUID
    last_service_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MaintenanceAlert(BaseModel):
    vehicle_id: UUID
    plate: str
    km_since_service: int
    interval_km: int
    severity: str  # "ok" | "due_soon" | "overdue"


class AutoAssignResult(BaseModel):
    route_id: UUID
    vehicle_id: UUID
    plate: str
    reason: str


class FleetSyncResult(BaseModel):
    pulled: int
    pushed: int
    timestamp: datetime
