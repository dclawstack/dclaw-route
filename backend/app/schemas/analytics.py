from uuid import UUID
from pydantic import BaseModel


class RoutePnLRead(BaseModel):
    route_id: UUID
    route_name: str
    total_distance_km: float
    estimated_minutes: int
    fuel_cost_usd: float
    labor_cost_usd: float
    vehicle_cost_usd: float
    total_cost_usd: float
    stop_count: int
    completed_count: int
    on_time_count: int
    miles_per_stop: float
    cost_per_delivery: float
    on_time_rate_pct: float


class FleetSummaryRead(BaseModel):
    route_count: int
    total_distance_km: float
    total_cost_usd: float
    avg_cost_per_delivery: float
    avg_on_time_rate_pct: float
    rates: dict[str, float]
