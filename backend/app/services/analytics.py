"""Cost + performance analytics.

Demo-ready stub. Per-route P&L using fixed unit rates and rough
performance metrics (on-time rate, miles per stop, cost per delivery).

Per PRD P2.3 / PLAN #7. Real impl pulls rates from a config table,
joins against real driver pay records and fuel receipts.
"""
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route import Route


# Unit rates — placeholders. Surfaced in the response so reviewers see
# what the cost model assumes.
FUEL_PER_KM_USD = 0.18
LABOR_PER_HOUR_USD = 25.00
VEHICLE_PER_KM_USD = 0.12
ON_TIME_BUFFER_MIN = 5


@dataclass
class RoutePnL:
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


@dataclass
class FleetSummary:
    route_count: int
    total_distance_km: float
    total_cost_usd: float
    avg_cost_per_delivery: float
    avg_on_time_rate_pct: float
    rates: dict[str, float]


def _route_pnl(route: Route) -> RoutePnL:
    fuel = route.total_distance_km * FUEL_PER_KM_USD
    labor = (route.estimated_minutes / 60.0) * LABOR_PER_HOUR_USD
    vehicle = route.total_distance_km * VEHICLE_PER_KM_USD
    total = fuel + labor + vehicle

    deliveries = route.deliveries or []
    stop_count = len(deliveries)
    completed = [d for d in deliveries if d.status == "completed"]
    completed_count = len(completed)

    # On-time: completed within budgeted time + buffer. Without a real
    # baseline ETA per stop we treat any completed delivery whose
    # completed_at is set as on-time. Approximation only.
    on_time_count = completed_count

    miles_per_stop = (
        (route.total_distance_km / stop_count) if stop_count else 0.0
    )
    cost_per_delivery = (total / stop_count) if stop_count else 0.0
    on_time_rate = (
        (on_time_count / completed_count * 100.0) if completed_count else 0.0
    )
    return RoutePnL(
        route_id=route.id,
        route_name=route.name,
        total_distance_km=route.total_distance_km,
        estimated_minutes=route.estimated_minutes,
        fuel_cost_usd=round(fuel, 2),
        labor_cost_usd=round(labor, 2),
        vehicle_cost_usd=round(vehicle, 2),
        total_cost_usd=round(total, 2),
        stop_count=stop_count,
        completed_count=completed_count,
        on_time_count=on_time_count,
        miles_per_stop=round(miles_per_stop, 2),
        cost_per_delivery=round(cost_per_delivery, 2),
        on_time_rate_pct=round(on_time_rate, 1),
    )


async def route_pnl(db: AsyncSession, route_id: UUID) -> RoutePnL:
    result = await db.execute(select(Route).where(Route.id == route_id))
    route = result.scalar_one_or_none()
    if route is None:
        raise ValueError("Route not found")
    return _route_pnl(route)


async def fleet_summary(db: AsyncSession) -> FleetSummary:
    result = await db.execute(select(Route))
    routes = list(result.scalars())
    pnls = [_route_pnl(r) for r in routes]
    total_dist = sum(p.total_distance_km for p in pnls)
    total_cost = sum(p.total_cost_usd for p in pnls)
    total_deliveries = sum(p.stop_count for p in pnls)
    avg_cost_per = (total_cost / total_deliveries) if total_deliveries else 0.0
    avg_on_time = (
        sum(p.on_time_rate_pct for p in pnls if p.completed_count > 0)
        / max(1, sum(1 for p in pnls if p.completed_count > 0))
        if any(p.completed_count > 0 for p in pnls)
        else 0.0
    )
    return FleetSummary(
        route_count=len(routes),
        total_distance_km=round(total_dist, 2),
        total_cost_usd=round(total_cost, 2),
        avg_cost_per_delivery=round(avg_cost_per, 2),
        avg_on_time_rate_pct=round(avg_on_time, 1),
        rates={
            "fuel_per_km_usd": FUEL_PER_KM_USD,
            "labor_per_hour_usd": LABOR_PER_HOUR_USD,
            "vehicle_per_km_usd": VEHICLE_PER_KM_USD,
        },
    )


async def all_routes_pnl(db: AsyncSession) -> list[RoutePnL]:
    result = await db.execute(select(Route))
    return [_route_pnl(r) for r in result.scalars()]
