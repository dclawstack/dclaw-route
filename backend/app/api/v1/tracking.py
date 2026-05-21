from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.utils import utc_now
from app.repositories.driver_repo import DriverRepository
from app.schemas.tracking import (
    DriverLocation,
    LocationPing,
    RouteETARead,
    StopETARead,
)
from app.services.eta_engine import compute_route_eta

router = APIRouter()


@router.post("/drivers/{driver_id}/location", response_model=DriverLocation)
async def update_driver_location(
    driver_id: UUID, payload: LocationPing, db: AsyncSession = Depends(get_db)
):
    repo = DriverRepository(db)
    driver = await repo.get_by_id(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.current_lat = payload.lat
    driver.current_lng = payload.lng
    driver.location_updated_at = utc_now()
    await db.commit()
    await db.refresh(driver)
    return DriverLocation(
        driver_id=driver.id,
        current_lat=driver.current_lat,
        current_lng=driver.current_lng,
        location_updated_at=driver.location_updated_at,
    )


@router.get("/routes/{route_id}/eta", response_model=RouteETARead)
async def get_route_eta(route_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await compute_route_eta(db, route_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return RouteETARead(
        route_id=result.route_id,
        driver_id=result.driver_id,
        driver_position=result.driver_position,
        stops=[StopETARead(**s.__dict__) for s in result.stops],
        is_delayed=result.is_delayed,
    )
