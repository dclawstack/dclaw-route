"""ETA engine.

Demo-ready stub. Given a driver's current GPS position and the pending
deliveries on their assigned route, computes a running ETA for each
stop using straight-line haversine distance at a fixed average speed.

Per PRD P0.3 acceptance criteria: ETA accuracy ±5min. Real implementation
will hit a routing engine (OSRM/Google) and factor in traffic.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import utc_now
from app.models.delivery import Delivery
from app.models.driver import Driver
from app.models.route import Route
from app.services.optimizer import haversine_km


AVG_SPEED_KMH = 30.0
DELAY_THRESHOLD_MINUTES = 15


@dataclass
class StopETA:
    delivery_id: UUID
    stop_id: UUID
    stop_name: str
    sequence: int
    distance_from_previous_km: float
    cumulative_km: float
    eta: datetime
    minutes_from_now: int


@dataclass
class RouteETA:
    route_id: UUID
    driver_id: UUID | None
    driver_position: tuple[float, float] | None
    stops: list[StopETA]
    is_delayed: bool


async def compute_route_eta(
    db: AsyncSession, route_id: UUID, now: datetime | None = None
) -> RouteETA:
    """Compute ETA for each pending delivery on a route."""
    current_time = now or utc_now()

    route_result = await db.execute(select(Route).where(Route.id == route_id))
    route = route_result.scalar_one_or_none()
    if route is None:
        raise ValueError("Route not found")

    driver: Driver | None = None
    driver_pos: tuple[float, float] | None = None
    if route.driver_id:
        d_result = await db.execute(select(Driver).where(Driver.id == route.driver_id))
        driver = d_result.scalar_one_or_none()
        if driver and driver.current_lat is not None and driver.current_lng is not None:
            driver_pos = (driver.current_lat, driver.current_lng)

    pending = sorted(
        [d for d in route.deliveries if d.status == "pending"],
        key=lambda d: d.sequence,
    )

    stops: list[StopETA] = []
    cumulative_km = 0.0
    cumulative_minutes = 0.0
    prev_point = driver_pos

    for delivery in pending:
        stop = delivery.stop
        if prev_point is not None:
            leg_km = haversine_km(prev_point[0], prev_point[1], stop.lat, stop.lng)
        else:
            leg_km = 0.0
        cumulative_km += leg_km
        leg_minutes = (leg_km / AVG_SPEED_KMH) * 60 if AVG_SPEED_KMH > 0 else 0
        cumulative_minutes += leg_minutes
        eta = current_time + timedelta(minutes=cumulative_minutes)
        stops.append(
            StopETA(
                delivery_id=delivery.id,
                stop_id=stop.id,
                stop_name=stop.name,
                sequence=delivery.sequence,
                distance_from_previous_km=round(leg_km, 2),
                cumulative_km=round(cumulative_km, 2),
                eta=eta,
                minutes_from_now=int(cumulative_minutes),
            )
        )
        prev_point = (stop.lat, stop.lng)

    is_delayed = bool(
        driver
        and driver.location_updated_at
        and (current_time - driver.location_updated_at).total_seconds() / 60
        > DELAY_THRESHOLD_MINUTES
    )

    return RouteETA(
        route_id=route_id,
        driver_id=route.driver_id,
        driver_position=driver_pos,
        stops=stops,
        is_delayed=is_delayed,
    )
