"""Autonomous vehicle dispatch service.

Demo-ready stub for PLAN-v1.2.md #11. Tracks an AV fleet and assigns
the highest-autopilot-level vehicle to a route on dispatch. Real impl
hits a vendor's AV fleet API (Waymo, Nuro, etc.).
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.av import AutonomousVehicle
from app.models.route import Route
from app.schemas.av import DispatchRequest, DispatchResult


async def dispatch_av(db: AsyncSession, req: DispatchRequest) -> DispatchResult:
    route_result = await db.execute(select(Route).where(Route.id == req.route_id))
    route = route_result.scalar_one_or_none()
    if route is None:
        raise ValueError("Route not found")

    avs_result = await db.execute(
        select(AutonomousVehicle).where(
            AutonomousVehicle.status == "available",
            AutonomousVehicle.autopilot_level >= req.min_autopilot_level,
        )
    )
    candidates = list(avs_result.scalars())
    if not candidates:
        raise ValueError("No available AV matching autopilot-level requirement")

    chosen = max(candidates, key=lambda v: v.autopilot_level)
    chosen.status = "dispatched"
    chosen.current_route_id = route.id
    await db.commit()
    return DispatchResult(
        av_id=chosen.id,
        vendor=chosen.vendor,
        model=chosen.model,
        autopilot_level=chosen.autopilot_level,
        route_id=route.id,
    )


async def recall_av(db: AsyncSession, av_id: UUID) -> AutonomousVehicle | None:
    result = await db.execute(
        select(AutonomousVehicle).where(AutonomousVehicle.id == av_id)
    )
    av = result.scalar_one_or_none()
    if av is None:
        return None
    av.status = "available"
    av.current_route_id = None
    await db.commit()
    await db.refresh(av)
    return av
