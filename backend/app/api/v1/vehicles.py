from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.vehicle import Vehicle
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.vehicle import (
    AutoAssignResult,
    FleetSyncResult,
    MaintenanceAlert,
    VehicleCreate,
    VehicleRead,
    VehicleUpdate,
)
from app.services.fleet_sync import (
    auto_assign_to_route,
    maintenance_alerts,
    sync_with_dclaw_fleet,
)

router = APIRouter()


@router.get("/", response_model=list[VehicleRead])
async def list_vehicles(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    repo = VehicleRepository(db)
    items, _ = await repo.list_all(limit=limit, offset=offset)
    return items


@router.post("/", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
async def create_vehicle(payload: VehicleCreate, db: AsyncSession = Depends(get_db)):
    repo = VehicleRepository(db)
    vehicle = Vehicle(**payload.model_dump())
    return await repo.create(vehicle)


@router.patch("/{vehicle_id}", response_model=VehicleRead)
async def update_vehicle(
    vehicle_id: UUID, payload: VehicleUpdate, db: AsyncSession = Depends(get_db)
):
    repo = VehicleRepository(db)
    vehicle = await repo.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(vehicle, k, v)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(vehicle_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = VehicleRepository(db)
    vehicle = await repo.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    await repo.delete(vehicle)


@router.get("/maintenance/alerts", response_model=list[MaintenanceAlert])
async def get_maintenance_alerts(db: AsyncSession = Depends(get_db)):
    return await maintenance_alerts(db)


@router.post("/auto-assign/{route_id}", response_model=AutoAssignResult)
async def auto_assign(route_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await auto_assign_to_route(db, route_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sync", response_model=FleetSyncResult)
async def sync(db: AsyncSession = Depends(get_db)):
    return await sync_with_dclaw_fleet(db)
