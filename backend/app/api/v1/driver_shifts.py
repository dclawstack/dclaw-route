from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.driver_shift import DriverShift
from app.repositories.driver_shift_repo import DriverShiftRepository
from app.schemas.driver_shift import (
    DriverShiftCreate,
    DriverShiftRead,
    DriverShiftUpdate,
    FatigueAlert,
)
from app.services.fatigue_monitor import alert_for_driver, alerts_for_all_drivers

router = APIRouter()


@router.get("/", response_model=list[DriverShiftRead])
async def list_shifts(
    driver_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(DriverShift)
    if driver_id is not None:
        stmt = stmt.where(DriverShift.driver_id == driver_id)
    stmt = stmt.order_by(DriverShift.start_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=DriverShiftRead, status_code=status.HTTP_201_CREATED)
async def create_shift(payload: DriverShiftCreate, db: AsyncSession = Depends(get_db)):
    repo = DriverShiftRepository(db)
    shift = DriverShift(**payload.model_dump())
    return await repo.create(shift)


@router.patch("/{shift_id}", response_model=DriverShiftRead)
async def update_shift(
    shift_id: UUID, payload: DriverShiftUpdate, db: AsyncSession = Depends(get_db)
):
    repo = DriverShiftRepository(db)
    shift = await repo.get_by_id(shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(shift, k, v)
    await db.commit()
    await db.refresh(shift)
    return shift


@router.delete("/{shift_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shift(shift_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = DriverShiftRepository(db)
    shift = await repo.get_by_id(shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    await repo.delete(shift)


@router.get("/fatigue/alerts", response_model=list[FatigueAlert])
async def fatigue_alerts(db: AsyncSession = Depends(get_db)):
    return await alerts_for_all_drivers(db)


@router.get("/fatigue/alerts/{driver_id}", response_model=FatigueAlert)
async def fatigue_alert_one(driver_id: UUID, db: AsyncSession = Depends(get_db)):
    alert = await alert_for_driver(db, driver_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Driver not found")
    return alert
