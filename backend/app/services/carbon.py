"""Carbon-optimized routing service.

Demo-ready stub for PLAN-v1.2.md #12. Computes per-route CO2 emissions
from vehicle emission factor × route distance, and picks the lowest-
emission available vehicle when asked to optimize for carbon.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route import Route
from app.models.vehicle import Vehicle
from app.schemas.carbon import (
    CarbonOptimizeResult,
    FleetEmissions,
    RouteEmissions,
)


async def _route_emissions(db: AsyncSession, route: Route) -> RouteEmissions:
    vehicle = None
    if route.vehicle_id:
        vresult = await db.execute(
            select(Vehicle).where(Vehicle.id == route.vehicle_id)
        )
        vehicle = vresult.scalar_one_or_none()
    co2_kg = (
        (route.total_distance_km * vehicle.co2_g_per_km) / 1000.0 if vehicle else 0.0
    )
    return RouteEmissions(
        route_id=route.id,
        route_name=route.name,
        total_distance_km=route.total_distance_km,
        vehicle_id=vehicle.id if vehicle else None,
        vehicle_plate=vehicle.plate if vehicle else None,
        co2_g_per_km=vehicle.co2_g_per_km if vehicle else None,
        co2_total_kg=round(co2_kg, 2),
    )


async def route_emissions(db: AsyncSession, route_id: UUID) -> RouteEmissions:
    result = await db.execute(select(Route).where(Route.id == route_id))
    route = result.scalar_one_or_none()
    if route is None:
        raise ValueError("Route not found")
    return await _route_emissions(db, route)


async def fleet_emissions(db: AsyncSession) -> FleetEmissions:
    result = await db.execute(select(Route))
    emissions = [await _route_emissions(db, r) for r in result.scalars()]
    total_co2 = sum(e.co2_total_kg for e in emissions)
    total_dist = sum(e.total_distance_km for e in emissions)
    avg = (
        (total_co2 * 1000.0 / total_dist) if total_dist > 0 else 0.0
    )  # g/km
    return FleetEmissions(
        total_co2_kg=round(total_co2, 2),
        total_distance_km=round(total_dist, 2),
        avg_co2_g_per_km=round(avg, 1),
        route_count=len(emissions),
    )


async def optimize_vehicle_for_carbon(
    db: AsyncSession, route_id: UUID
) -> CarbonOptimizeResult:
    """Pick the lowest-emission available vehicle and assign it."""
    route_result = await db.execute(select(Route).where(Route.id == route_id))
    route = route_result.scalar_one_or_none()
    if route is None:
        raise ValueError("Route not found")

    # Treat any vehicle currently on a non-completed route as busy.
    busy_result = await db.execute(
        select(Route.vehicle_id).where(
            Route.vehicle_id.is_not(None),
            Route.status.in_(["planned", "in_progress"]),
            Route.id != route.id,
        )
    )
    busy_ids = {row[0] for row in busy_result if row[0] is not None}

    candidates_result = await db.execute(
        select(Vehicle).where(Vehicle.status == "available")
    )
    candidates = [v for v in candidates_result.scalars() if v.id not in busy_ids]
    if not candidates:
        raise ValueError("No available vehicle")

    chosen = min(candidates, key=lambda v: v.co2_g_per_km)
    worst = max(candidates, key=lambda v: v.co2_g_per_km)
    co2_saved = (
        (route.total_distance_km * (worst.co2_g_per_km - chosen.co2_g_per_km))
        / 1000.0
    )

    route.vehicle_id = chosen.id
    await db.commit()
    return CarbonOptimizeResult(
        route_id=route.id,
        chosen_vehicle_id=chosen.id,
        chosen_plate=chosen.plate,
        chosen_co2_g_per_km=chosen.co2_g_per_km,
        co2_saved_kg=round(co2_saved, 2),
    )
