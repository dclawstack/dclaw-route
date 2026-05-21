"""Multi-constraint route optimization service.

Demo-ready stub: nearest-neighbor heuristic over haversine distance,
with a `max_stops` soft constraint. Honors a single anchor (first stop
stays first) so optimization is deterministic for the same input.

OR-Tools is in requirements.txt for the upgrade path; the real VRP
solver lands when we wire in time windows, capacity, and driver skills.
"""
import math
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery import Delivery
from app.repositories.route_repo import RouteRepository


EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    lat1r, lat2r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1r) * math.cos(lat2r) * math.sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


@dataclass
class OptimizeResult:
    original_sequence: list[UUID]
    optimized_sequence: list[UUID]
    original_distance_km: float
    optimized_distance_km: float
    improvement_percent: float


def _total_distance(points: list[tuple[float, float]]) -> float:
    return sum(
        haversine_km(*points[i], *points[i + 1]) for i in range(len(points) - 1)
    )


def _nearest_neighbor(
    points: list[tuple[float, float]], anchor_first: bool = True
) -> list[int]:
    """Return permutation of indices in nearest-neighbor order.

    If anchor_first, index 0 stays at position 0 (useful when the first
    stop is the depot or warehouse).
    """
    n = len(points)
    if n <= 1:
        return list(range(n))
    start = 0 if anchor_first else 0
    visited = {start}
    order = [start]
    current = start
    while len(visited) < n:
        best_idx = -1
        best_dist = float("inf")
        for i in range(n):
            if i in visited:
                continue
            d = haversine_km(*points[current], *points[i])
            if d < best_dist:
                best_dist = d
                best_idx = i
        order.append(best_idx)
        visited.add(best_idx)
        current = best_idx
    return order


async def optimize_route(
    db: AsyncSession, route_id: UUID, max_stops: int | None = None
) -> OptimizeResult:
    """Optimize the delivery sequence for a route.

    Reorders deliveries in-place by sequence. Returns before/after stats.
    Raises ValueError if the route isn't found or has fewer than 2 stops.
    """
    repo = RouteRepository(db)
    route = await repo.get_by_id(route_id)
    if route is None:
        raise ValueError("Route not found")

    deliveries: list[Delivery] = sorted(route.deliveries, key=lambda d: d.sequence)
    if max_stops is not None:
        deliveries = deliveries[:max_stops]
    if len(deliveries) < 2:
        raise ValueError("Route needs at least 2 stops to optimize")

    points = [(d.stop.lat, d.stop.lng) for d in deliveries]
    original_seq = [d.id for d in deliveries]
    original_dist = _total_distance(points)

    order = _nearest_neighbor(points, anchor_first=True)
    optimized_points = [points[i] for i in order]
    optimized_seq = [deliveries[i].id for i in order]
    optimized_dist = _total_distance(optimized_points)

    for new_pos, old_idx in enumerate(order):
        deliveries[old_idx].sequence = new_pos

    route.total_distance_km = round(optimized_dist, 2)
    route.estimated_minutes = int(optimized_dist * 2)  # rough: 30 km/h average
    await db.commit()

    improvement = (
        0.0
        if original_dist == 0
        else ((original_dist - optimized_dist) / original_dist) * 100
    )
    return OptimizeResult(
        original_sequence=original_seq,
        optimized_sequence=optimized_seq,
        original_distance_km=round(original_dist, 2),
        optimized_distance_km=round(optimized_dist, 2),
        improvement_percent=round(improvement, 1),
    )
