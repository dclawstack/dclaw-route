from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DriverShiftBase(BaseModel):
    driver_id: UUID
    start_at: datetime
    end_at: datetime | None = None
    hours_worked: float = 0.0
    status: str = "scheduled"


class DriverShiftCreate(DriverShiftBase):
    pass


class DriverShiftUpdate(BaseModel):
    end_at: datetime | None = None
    hours_worked: float | None = None
    status: str | None = None


class DriverShiftRead(DriverShiftBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FatigueAlert(BaseModel):
    driver_id: UUID
    driver_name: str
    hours_last_7_days: float
    limit_hours: float
    remaining_hours: float
    severity: str  # "ok" | "warning" | "critical"
