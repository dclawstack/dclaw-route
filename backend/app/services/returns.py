"""Returns / reverse-logistics service.

Demo-ready stub. Returns are stored as Delivery rows with kind="pickup"
on a system-generated "Pickup queue" route. The consolidate operation
groups all pending pickups into a new route ordered by nearest-neighbor.

PRD §6 P1.4 calls for AI return-route optimization + consolidation —
this uses the same greedy heuristic as the regular optimizer.
"""
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import utc_now
from app.models.delivery import Delivery
from app.models.route import Route
from app.models.stop import Stop
from app.schemas.returns import ConsolidationResult
from app.services.optimizer import _nearest_neighbor, _total_distance


QUEUE_ROUTE_NAME = "Pickup queue"


async def _get_or_create_queue_route(db: AsyncSession) -> Route:
    result = await db.execute(select(Route).where(Route.name == QUEUE_ROUTE_NAME))
    queue = result.scalar_one_or_none()
    if queue:
        return queue
    queue = Route(name=QUEUE_ROUTE_NAME, status="planned")
    db.add(queue)
    await db.commit()
    await db.refresh(queue)
    return queue


async def request_return(
    db: AsyncSession, stop_id: UUID, notes: str | None = None
) -> Delivery:
    queue = await _get_or_create_queue_route(db)
    seq_result = await db.execute(
        select(Delivery).where(Delivery.route_id == queue.id)
    )
    seq = len(list(seq_result.scalars().all()))
    delivery = Delivery(
        route_id=queue.id,
        stop_id=stop_id,
        sequence=seq,
        kind="pickup",
        status="pending",
        notes=notes,
    )
    db.add(delivery)
    await db.commit()
    await db.refresh(delivery)
    return delivery


async def list_pending_returns(db: AsyncSession) -> list[Delivery]:
    queue_result = await db.execute(select(Route).where(Route.name == QUEUE_ROUTE_NAME))
    queue = queue_result.scalar_one_or_none()
    if not queue:
        return []
    result = await db.execute(
        select(Delivery)
        .where(Delivery.route_id == queue.id, Delivery.status == "pending")
        .order_by(Delivery.created_at)
    )
    return list(result.scalars().all())


async def consolidate_returns(db: AsyncSession) -> ConsolidationResult:
    """Move all pending queue pickups onto a fresh route in NN order."""
    pickups = await list_pending_returns(db)
    if len(pickups) < 2:
        raise ValueError("Need at least 2 pending returns to consolidate")

    # Resolve stop coordinates.
    stop_ids = [p.stop_id for p in pickups]
    stops_result = await db.execute(select(Stop).where(Stop.id.in_(stop_ids)))
    stops = {s.id: s for s in stops_result.scalars()}
    points = [(stops[p.stop_id].lat, stops[p.stop_id].lng) for p in pickups]

    order = _nearest_neighbor(points, anchor_first=True)
    optimized_points = [points[i] for i in order]
    total_km = _total_distance(optimized_points)

    new_name = f"Return run {date.today().isoformat()}"
    new_route = Route(
        name=new_name,
        status="planned",
        total_distance_km=round(total_km, 2),
        estimated_minutes=int(total_km * 2),
    )
    db.add(new_route)
    await db.flush()

    for new_pos, old_idx in enumerate(order):
        pickup = pickups[old_idx]
        pickup.route_id = new_route.id
        pickup.sequence = new_pos

    await db.commit()
    return ConsolidationResult(
        route_id=new_route.id,
        route_name=new_route.name,
        consolidated_count=len(pickups),
        total_distance_km=new_route.total_distance_km,
        estimated_minutes=new_route.estimated_minutes,
    )
