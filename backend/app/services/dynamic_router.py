"""Dynamic rerouting service.

Demo-ready stub. Insert a new urgent stop into an existing route at
the position that minimizes added distance (cheapest-insertion). Also
estimates the ETA-shift impact on every subsequent pending stop.

PRD §7 P2.2 calls for traffic/accident-aware rerouting in <10s. This
covers the "new urgent order" case; traffic-driven reroute deferred.
"""
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery import Delivery
from app.models.route import Route
from app.models.stop import Stop
from app.services.eta_engine import AVG_SPEED_KMH
from app.services.optimizer import haversine_km


@dataclass
class StopImpact:
    delivery_id: UUID
    stop_name: str
    old_sequence: int
    new_sequence: int
    eta_shift_minutes: int


@dataclass
class InsertResult:
    route_id: UUID
    inserted_delivery_id: UUID
    inserted_at_position: int
    extra_distance_km: float
    extra_minutes: int
    shifted_stops: list[StopImpact]


async def insert_urgent_stop(
    db: AsyncSession, route_id: UUID, stop_id: UUID
) -> InsertResult:
    """Insert a new urgent stop into a route at the cheapest position.

    Operates only on PENDING deliveries (completed ones aren't reordered).
    """
    route_result = await db.execute(select(Route).where(Route.id == route_id))
    route = route_result.scalar_one_or_none()
    if route is None:
        raise ValueError("Route not found")

    stop_result = await db.execute(select(Stop).where(Stop.id == stop_id))
    new_stop = stop_result.scalar_one_or_none()
    if new_stop is None:
        raise ValueError("Stop not found")

    pending = sorted(
        [d for d in route.deliveries if d.status == "pending"],
        key=lambda d: d.sequence,
    )
    points = [(d.stop.lat, d.stop.lng) for d in pending]
    new_point = (new_stop.lat, new_stop.lng)

    # Cheapest-insertion: find position k that minimizes
    # d(prev, new) + d(new, next) - d(prev, next).
    if not points:
        best_k = 0
        best_extra = 0.0
    else:
        best_k = 0
        # Default: insert at start.
        best_extra = haversine_km(*new_point, *points[0])
        for k in range(1, len(points)):
            extra = (
                haversine_km(*points[k - 1], *new_point)
                + haversine_km(*new_point, *points[k])
                - haversine_km(*points[k - 1], *points[k])
            )
            if extra < best_extra:
                best_extra = extra
                best_k = k
        # Also consider appending at the end.
        end_extra = haversine_km(*points[-1], *new_point)
        if end_extra < best_extra:
            best_extra = end_extra
            best_k = len(points)

    # Build the new delivery row at the right sequence.
    new_delivery = Delivery(
        route_id=route.id,
        stop_id=new_stop.id,
        sequence=best_k,
        kind="drop_off",
        status="pending",
    )

    # Shift subsequent pending stops by +1 and record their impact.
    shifted: list[StopImpact] = []
    extra_minutes = int((best_extra / AVG_SPEED_KMH) * 60) if AVG_SPEED_KMH else 0
    for d in pending:
        if d.sequence >= best_k:
            old_seq = d.sequence
            d.sequence = old_seq + 1
            shifted.append(
                StopImpact(
                    delivery_id=d.id,
                    stop_name=d.stop.name,
                    old_sequence=old_seq,
                    new_sequence=d.sequence,
                    eta_shift_minutes=extra_minutes,
                )
            )

    db.add(new_delivery)
    route.total_distance_km = round(route.total_distance_km + best_extra, 2)
    route.estimated_minutes = route.estimated_minutes + extra_minutes
    await db.commit()
    await db.refresh(new_delivery)

    return InsertResult(
        route_id=route.id,
        inserted_delivery_id=new_delivery.id,
        inserted_at_position=best_k,
        extra_distance_km=round(best_extra, 2),
        extra_minutes=extra_minutes,
        shifted_stops=shifted,
    )
