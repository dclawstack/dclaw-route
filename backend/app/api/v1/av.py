from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.av import AutonomousVehicle
from app.schemas.av import (
    AvCreate,
    AvRead,
    AvUpdate,
    DispatchRequest,
    DispatchResult,
)
from app.services.av_dispatch import dispatch_av, recall_av

router = APIRouter()


@router.get("/", response_model=list[AvRead])
async def list_avs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AutonomousVehicle))
    return list(result.scalars().all())


@router.post("/", response_model=AvRead, status_code=status.HTTP_201_CREATED)
async def create_av(payload: AvCreate, db: AsyncSession = Depends(get_db)):
    av = AutonomousVehicle(**payload.model_dump())
    db.add(av)
    await db.commit()
    await db.refresh(av)
    return av


@router.patch("/{av_id}", response_model=AvRead)
async def update_av(av_id: UUID, payload: AvUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AutonomousVehicle).where(AutonomousVehicle.id == av_id)
    )
    av = result.scalar_one_or_none()
    if not av:
        raise HTTPException(status_code=404, detail="AV not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(av, k, v)
    await db.commit()
    await db.refresh(av)
    return av


@router.post("/dispatch", response_model=DispatchResult)
async def dispatch(payload: DispatchRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await dispatch_av(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/recall/{av_id}", response_model=AvRead)
async def recall(av_id: UUID, db: AsyncSession = Depends(get_db)):
    av = await recall_av(db, av_id)
    if av is None:
        raise HTTPException(status_code=404, detail="AV not found")
    return av
