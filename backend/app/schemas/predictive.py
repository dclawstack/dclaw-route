from uuid import UUID
from pydantic import BaseModel


class WeatherUpdate(BaseModel):
    factor: float  # 1.0 = clear, >1 = adverse, <1 = better than usual


class WeatherState(BaseModel):
    factor: float


class RouteForecastRead(BaseModel):
    route_id: UUID
    route_name: str
    hour: int
    traffic_factor: float
    weather_factor: float
    combined_factor: float
    baseline_minutes: int
    adjusted_minutes: int
