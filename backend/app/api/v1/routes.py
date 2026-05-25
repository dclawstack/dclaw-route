from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.route import Route
from app.models.delivery import Delivery
from app.repositories.route_repo import RouteRepository
from app.schemas.route import RouteCreate, RouteRead, RouteUpdate
from app.schemas.dynamic import (
    InsertResultRead,
    InsertUrgentRequest,
    StopImpactRead,
)
from app.schemas.optimizer import OptimizeRequest, OptimizeResponse
from app.services.dynamic_router import insert_urgent_stop
from app.services.optimizer import optimize_route

router = APIRouter()


@router.get("/", response_model=list[RouteRead])
async def list_routes(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    repo = RouteRepository(db)
    items, _ = await repo.list_all(limit=limit, offset=offset)
    return items


@router.post("/", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
async def create_route(payload: RouteCreate, db: AsyncSession = Depends(get_db)):
    route = Route(
        name=payload.name,
        driver_id=payload.driver_id,
        vehicle_id=payload.vehicle_id,
        status=payload.status,
        total_distance_km=payload.total_distance_km,
        estimated_minutes=payload.estimated_minutes,
        dock_number=payload.dock_number,
    )
    db.add(route)
    await db.flush()
    for idx, stop_id in enumerate(payload.stop_ids):
        db.add(Delivery(route_id=route.id, stop_id=stop_id, sequence=idx))
    await db.commit()
    await db.refresh(route)
    return route


@router.get("/{route_id}", response_model=RouteRead)
async def get_route(route_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = RouteRepository(db)
    route = await repo.get_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.patch("/{route_id}", response_model=RouteRead)
async def update_route(route_id: UUID, payload: RouteUpdate, db: AsyncSession = Depends(get_db)):
    repo = RouteRepository(db)
    route = await repo.get_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(route, k, v)
    await db.commit()
    await db.refresh(route)
    return route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(route_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = RouteRepository(db)
    route = await repo.get_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    await repo.delete(route)


@router.post("/{route_id}/optimize", response_model=OptimizeResponse)
async def optimize(
    route_id: UUID,
    payload: OptimizeRequest = OptimizeRequest(),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await optimize_route(db, route_id, max_stops=payload.max_stops)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return OptimizeResponse(route_id=route_id, **result.__dict__)


@router.post("/{route_id}/insert-urgent", response_model=InsertResultRead)
async def insert_urgent(
    route_id: UUID,
    payload: InsertUrgentRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await insert_urgent_stop(db, route_id, payload.stop_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return InsertResultRead(
        route_id=result.route_id,
        inserted_delivery_id=result.inserted_delivery_id,
        inserted_at_position=result.inserted_at_position,
        extra_distance_km=result.extra_distance_km,
        extra_minutes=result.extra_minutes,
        shifted_stops=[StopImpactRead(**s.__dict__) for s in result.shifted_stops],
    )
