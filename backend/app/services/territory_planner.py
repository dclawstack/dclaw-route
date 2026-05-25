"""Territory clustering service.

Demo-ready stub: vanilla k-means on stop coordinates. Real impl per
PRD P2.1 / PLAN #5 should weight by demand volume, drive time, and
customer density, and respect existing geographic boundaries.
"""
import random
from itertools import cycle
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stop import Stop
from app.models.territory import Territory
from app.schemas.territory import ClusterResult, TerritoryAssignment
from app.services.optimizer import haversine_km


DEFAULT_COLORS = ["#10B981", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]


def _kmeans(
    points: list[tuple[float, float]], k: int, max_iter: int = 20, seed: int = 42
) -> tuple[list[int], list[tuple[float, float]], int]:
    """Returns (assignments, centroids, iterations_used)."""
    if k <= 0 or len(points) == 0:
        return [], [], 0
    if k >= len(points):
        return list(range(len(points))), list(points), 0

    rng = random.Random(seed)
    centroids = rng.sample(points, k)
    assignments = [0] * len(points)
    for it in range(max_iter):
        # Assign each point to nearest centroid (haversine).
        new_assign = []
        for p in points:
            best = 0
            best_d = float("inf")
            for ci, c in enumerate(centroids):
                d = haversine_km(p[0], p[1], c[0], c[1])
                if d < best_d:
                    best_d = d
                    best = ci
            new_assign.append(best)
        if new_assign == assignments and it > 0:
            return assignments, centroids, it
        assignments = new_assign
        # Recompute centroids as cluster means.
        for ci in range(k):
            cluster_points = [p for p, a in zip(points, assignments) if a == ci]
            if cluster_points:
                lat = sum(p[0] for p in cluster_points) / len(cluster_points)
                lng = sum(p[1] for p in cluster_points) / len(cluster_points)
                centroids[ci] = (lat, lng)
    return assignments, centroids, max_iter


async def cluster_stops(
    db: AsyncSession, n: int, max_iter: int = 20
) -> ClusterResult:
    stops_result = await db.execute(select(Stop))
    stops = list(stops_result.scalars())
    if not stops:
        raise ValueError("No stops to cluster")
    if n < 1:
        raise ValueError("n must be >= 1")

    points = [(s.lat, s.lng) for s in stops]
    assigns, centroids, iters = _kmeans(points, n, max_iter)

    # Build or reuse territories: replace existing seeded territories with k new.
    existing_result = await db.execute(select(Territory))
    for t in existing_result.scalars():
        await db.delete(t)
    await db.flush()

    color_iter = cycle(DEFAULT_COLORS)
    territories: list[Territory] = []
    for i in range(n):
        t = Territory(name=f"Territory {i + 1}", color=next(color_iter))
        db.add(t)
        territories.append(t)
    await db.flush()

    for stop, cluster_idx in zip(stops, assigns):
        stop.territory_id = territories[cluster_idx].id

    await db.commit()

    summaries: list[TerritoryAssignment] = []
    for i, t in enumerate(territories):
        cluster_points = [p for p, a in zip(points, assigns) if a == i]
        summaries.append(
            TerritoryAssignment(
                territory_id=t.id,
                name=t.name,
                color=t.color,
                stop_count=len(cluster_points),
                center_lat=round(centroids[i][0], 4),
                center_lng=round(centroids[i][1], 4),
            )
        )
    return ClusterResult(
        territories=summaries, assigned_stops=len(stops), iterations=iters
    )


async def update_assignment(
    db: AsyncSession, stop_id: UUID, territory_id: UUID | None
) -> Stop | None:
    stop_result = await db.execute(select(Stop).where(Stop.id == stop_id))
    stop = stop_result.scalar_one_or_none()
    if not stop:
        return None
    stop.territory_id = territory_id
    await db.commit()
    await db.refresh(stop)
    return stop
