"""Predictive traffic + weather modifier service.

Demo-ready stub. Returns a multiplier applied to ETA estimates.
  - Hour-of-day congestion: peak rush hours (7-9 AM, 4-6 PM) = 1.5x,
    business hours = 1.1x, late night (10 PM-5 AM) = 0.85x, other = 1.0.
  - Weather: in-memory override (default 1.0 = clear). Production
    plugs in a real weather API (NWS, OpenWeather).
"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import utc_now
from app.models.route import Route


_weather_factor: float = 1.0  # module-level override; reset on each process start.


def set_weather_factor(factor: float) -> None:
    global _weather_factor
    if factor <= 0:
        raise ValueError("Weather factor must be > 0")
    _weather_factor = factor


def get_weather_factor() -> float:
    return _weather_factor


def traffic_factor(hour: int) -> float:
    if 7 <= hour < 10 or 16 <= hour < 19:
        return 1.5
    if 22 <= hour or hour < 5:
        return 0.85
    if 10 <= hour < 16:
        return 1.1
    return 1.0


@dataclass
class RouteForecast:
    route_id: UUID
    route_name: str
    hour: int
    traffic_factor: float
    weather_factor: float
    combined_factor: float
    baseline_minutes: int
    adjusted_minutes: int


async def forecast_route(
    db: AsyncSession, route_id: UUID, at: datetime | None = None
) -> RouteForecast:
    when = at or utc_now()
    result = await db.execute(select(Route).where(Route.id == route_id))
    route = result.scalar_one_or_none()
    if route is None:
        raise ValueError("Route not found")

    tf = traffic_factor(when.hour)
    wf = _weather_factor
    combined = round(tf * wf, 2)
    return RouteForecast(
        route_id=route.id,
        route_name=route.name,
        hour=when.hour,
        traffic_factor=tf,
        weather_factor=wf,
        combined_factor=combined,
        baseline_minutes=route.estimated_minutes,
        adjusted_minutes=int(route.estimated_minutes * combined),
    )
