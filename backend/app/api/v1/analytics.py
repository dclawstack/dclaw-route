from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.analytics import FleetSummaryRead, RoutePnLRead
from app.services.analytics import all_routes_pnl, fleet_summary, route_pnl

router = APIRouter()


@router.get("/routes", response_model=list[RoutePnLRead])
async def routes_pnl(db: AsyncSession = Depends(get_db)):
    pnls = await all_routes_pnl(db)
    return [RoutePnLRead(**p.__dict__) for p in pnls]


@router.get("/routes/{route_id}/pnl", response_model=RoutePnLRead)
async def one_route_pnl(route_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        pnl = await route_pnl(db, route_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return RoutePnLRead(**pnl.__dict__)


@router.get("/summary", response_model=FleetSummaryRead)
async def summary(db: AsyncSession = Depends(get_db)):
    s = await fleet_summary(db)
    return FleetSummaryRead(**s.__dict__)
