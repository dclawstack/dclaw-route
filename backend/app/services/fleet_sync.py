"""Fleet integration service.

Demo-ready stub for the DClaw Fleet integration. Includes:
  - Maintenance alerts based on km since last service.
  - Auto-assignment of an available vehicle to a route.
  - Sync stub (no real downstream — returns the current fleet snapshot).

Real impl will hit the DClaw Fleet HTTP API on every sync and push
utilization metrics back.
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import utc_now
from app.models.route import Route
from app.models.vehicle import Vehicle
from app.schemas.vehicle import (
    AutoAssignResult,
    FleetSyncResult,
    MaintenanceAlert,
)


SERVICE_INTERVAL_KM = 10000
DUE_SOON_THRESHOLD_KM = 9000


def _severity(km_since_service: int) -> str:
    if km_since_service >= SERVICE_INTERVAL_KM:
        return "overdue"
    if km_since_service >= DUE_SOON_THRESHOLD_KM:
        return "due_soon"
    return "ok"


async def maintenance_alerts(db: AsyncSession) -> list[MaintenanceAlert]:
    result = await db.execute(select(Vehicle))
    out: list[MaintenanceAlert] = []
    for v in result.scalars():
        km = max(0, v.odometer_km - v.last_service_odometer_km)
        out.append(
            MaintenanceAlert(
                vehicle_id=v.id,
                plate=v.plate,
                km_since_service=km,
                interval_km=SERVICE_INTERVAL_KM,
                severity=_severity(km),
            )
        )
    return out


async def auto_assign_to_route(db: AsyncSession, route_id: UUID) -> AutoAssignResult:
    """Pick the available vehicle with highest unused capacity and assign it."""
    route_result = await db.execute(select(Route).where(Route.id == route_id))
    route = route_result.scalar_one_or_none()
    if route is None:
        raise ValueError("Route not found")

    # Pick a vehicle not already assigned to an active route, with status=available.
    busy_ids = await db.execute(
        select(Route.vehicle_id).where(
            Route.vehicle_id.is_not(None), Route.status.in_(["planned", "in_progress"])
        )
    )
    busy = {row[0] for row in busy_ids if row[0] is not None}
    candidates_result = await db.execute(
        select(Vehicle).where(Vehicle.status == "available")
    )
    candidates = [v for v in candidates_result.scalars() if v.id not in busy]
    if not candidates:
        raise ValueError("No available vehicle")

    pick = max(candidates, key=lambda v: v.capacity_kg)
    route.vehicle_id = pick.id
    await db.commit()
    return AutoAssignResult(
        route_id=route.id,
        vehicle_id=pick.id,
        plate=pick.plate,
        reason=f"Selected vehicle with highest capacity ({pick.capacity_kg:.0f} kg)",
    )


async def sync_with_dclaw_fleet(db: AsyncSession) -> FleetSyncResult:
    """No-op stub sync. Returns counts so the UI shows something."""
    total = (await db.execute(select(func.count()).select_from(Vehicle))).scalar() or 0
    return FleetSyncResult(pulled=total, pushed=0, timestamp=utc_now())
