from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.carbon import (
    CarbonOptimizeResult,
    FleetEmissions,
    RouteEmissions,
)
from app.services.carbon import (
    fleet_emissions,
    optimize_vehicle_for_carbon,
    route_emissions,
)

router = APIRouter()


@router.get("/routes/{route_id}/emissions", response_model=RouteEmissions)
async def get_route_emissions(route_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await route_emissions(db, route_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/summary", response_model=FleetEmissions)
async def get_summary(db: AsyncSession = Depends(get_db)):
    return await fleet_emissions(db)


@router.post(
    "/routes/{route_id}/optimize-vehicle", response_model=CarbonOptimizeResult
)
async def optimize_vehicle(route_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await optimize_vehicle_for_carbon(db, route_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
