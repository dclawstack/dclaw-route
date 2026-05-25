"""Crowdsourced delivery service.

Demo-ready stub for PLAN-v1.2.md #10 ("Crowdsourced Delivery Network").
A pool of gig drivers can take overflow routes when full-time drivers
are out of capacity.

Selection rule: among gig drivers with status=available, vehicle_type
match (if requested), and rating >= min_rating, pick the nearest to
the requested location (if provided) or the highest rated.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gig_driver import GigDriver
from app.models.route import Route
from app.schemas.gig import GigAssignment, GigRequest
from app.services.optimizer import haversine_km


async def request_gig_driver(db: AsyncSession, req: GigRequest) -> GigAssignment:
    route_result = await db.execute(select(Route).where(Route.id == req.route_id))
    route = route_result.scalar_one_or_none()
    if route is None:
        raise ValueError("Route not found")

    candidates_result = await db.execute(
        select(GigDriver).where(
            GigDriver.status == "available", GigDriver.rating >= req.min_rating
        )
    )
    candidates = list(candidates_result.scalars())
    if req.vehicle_type:
        candidates = [g for g in candidates if g.vehicle_type == req.vehicle_type]
    if not candidates:
        raise ValueError("No available gig driver matching criteria")

    chosen: GigDriver
    distance_km: float | None
    if req.near_lat is not None and req.near_lng is not None:
        with_distance = [
            (
                g,
                haversine_km(req.near_lat, req.near_lng, g.current_lat, g.current_lng)
                if g.current_lat is not None and g.current_lng is not None
                else float("inf"),
            )
            for g in candidates
        ]
        with_distance.sort(key=lambda x: x[1])
        chosen, dist = with_distance[0]
        distance_km = None if dist == float("inf") else round(dist, 2)
    else:
        chosen = max(candidates, key=lambda g: g.rating)
        distance_km = None

    chosen.status = "busy"
    chosen.current_route_id = route.id
    await db.commit()

    return GigAssignment(
        gig_driver_id=chosen.id,
        gig_driver_name=chosen.name,
        rating=chosen.rating,
        vehicle_type=chosen.vehicle_type,
        distance_km=distance_km,
        route_id=route.id,
    )


async def release_gig_driver(db: AsyncSession, gig_id: UUID) -> GigDriver | None:
    result = await db.execute(select(GigDriver).where(GigDriver.id == gig_id))
    g = result.scalar_one_or_none()
    if g is None:
        return None
    g.status = "available"
    g.current_route_id = None
    await db.commit()
    await db.refresh(g)
    return g
