from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.returns import (
    ConsolidationResult,
    ReturnPickupRead,
    ReturnRequestPayload,
)
from app.services.returns import (
    consolidate_returns,
    list_pending_returns,
    request_return,
)

router = APIRouter()


@router.post("/request", response_model=ReturnPickupRead)
async def create_return_request(
    payload: ReturnRequestPayload, db: AsyncSession = Depends(get_db)
):
    return await request_return(db, payload.stop_id, payload.notes)


@router.get("/pending", response_model=list[ReturnPickupRead])
async def get_pending_returns(db: AsyncSession = Depends(get_db)):
    return await list_pending_returns(db)


@router.post("/consolidate", response_model=ConsolidationResult)
async def consolidate(db: AsyncSession = Depends(get_db)):
    try:
        return await consolidate_returns(db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
