from uuid import UUID
from pydantic import BaseModel


class RouteEmissions(BaseModel):
    route_id: UUID
    route_name: str
    total_distance_km: float
    vehicle_id: UUID | None
    vehicle_plate: str | None
    co2_g_per_km: float | None
    co2_total_kg: float


class FleetEmissions(BaseModel):
    total_co2_kg: float
    total_distance_km: float
    avg_co2_g_per_km: float
    route_count: int


class CarbonOptimizeResult(BaseModel):
    route_id: UUID
    chosen_vehicle_id: UUID
    chosen_plate: str
    chosen_co2_g_per_km: float
    co2_saved_kg: float  # vs the most-polluting candidate, for illustration
