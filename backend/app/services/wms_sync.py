"""WMS integration service.

Demo-ready stub for the DClaw WMS integration. Provides:
  - loading_manifest(): the LIFO loading order for a route (last stop
    loads first → deepest in the truck; first stop loads last → closest
    to the door).
  - assign_dock(): persist a loading-dock identifier on a route.
  - sync_with_wms(): no-op snapshot stub.

PRD §7 P2.4 calls for full optimized loading + dispatch scheduling +
dock coordination. The LIFO heuristic covers the common case; smarter
ordering (by weight/size/temperature zone) is deferred.
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import utc_now
from app.models.delivery import Delivery
from app.models.route import Route
from app.schemas.wms import (
    DockAssignment,
    LoadingItem,
    LoadingManifest,
    WmsSyncResult,
)


async def loading_manifest(db: AsyncSession, route_id: UUID) -> LoadingManifest:
    result = await db.execute(select(Route).where(Route.id == route_id))
    route = result.scalar_one_or_none()
    if route is None:
        raise ValueError("Route not found")

    # LIFO: last stop loaded first, first stop loaded last. So sort by
    # sequence DESC and use that index as load_position (0 = closest to door).
    deliveries = sorted(route.deliveries or [], key=lambda d: d.sequence, reverse=True)
    items = [
        LoadingItem(
            delivery_id=d.id,
            stop_id=d.stop_id,
            stop_name=d.stop.name,
            load_position=i,
            delivery_sequence=d.sequence,
        )
        for i, d in enumerate(deliveries)
    ]
    return LoadingManifest(
        route_id=route.id,
        route_name=route.name,
        dock_number=route.dock_number,
        item_count=len(items),
        items=items,
    )


async def assign_dock(
    db: AsyncSession, route_id: UUID, dock_number: str
) -> DockAssignment:
    result = await db.execute(select(Route).where(Route.id == route_id))
    route = result.scalar_one_or_none()
    if route is None:
        raise ValueError("Route not found")
    route.dock_number = dock_number
    await db.commit()
    return DockAssignment(route_id=route.id, dock_number=dock_number)


async def sync_with_wms(db: AsyncSession) -> WmsSyncResult:
    routes = (await db.execute(select(func.count()).select_from(Route))).scalar() or 0
    deliveries = (
        await db.execute(select(func.count()).select_from(Delivery))
    ).scalar() or 0
    return WmsSyncResult(
        routes_synced=routes, deliveries_synced=deliveries, timestamp=utc_now()
    )
