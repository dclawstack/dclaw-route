from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.gig_driver import GigDriver
from app.schemas.gig import (
    GigAssignment,
    GigDriverCreate,
    GigDriverRead,
    GigDriverUpdate,
    GigRequest,
)
from app.services.gig import release_gig_driver, request_gig_driver

router = APIRouter()


@router.get("/drivers", response_model=list[GigDriverRead])
async def list_gig_drivers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GigDriver))
    return list(result.scalars().all())


@router.post("/drivers", response_model=GigDriverRead, status_code=status.HTTP_201_CREATED)
async def create_gig_driver(payload: GigDriverCreate, db: AsyncSession = Depends(get_db)):
    g = GigDriver(**payload.model_dump())
    db.add(g)
    await db.commit()
    await db.refresh(g)
    return g


@router.patch("/drivers/{gig_id}", response_model=GigDriverRead)
async def update_gig_driver(
    gig_id: UUID, payload: GigDriverUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(GigDriver).where(GigDriver.id == gig_id))
    g = result.scalar_one_or_none()
    if not g:
        raise HTTPException(status_code=404, detail="Gig driver not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(g, k, v)
    await db.commit()
    await db.refresh(g)
    return g


@router.post("/request", response_model=GigAssignment)
async def request_gig(payload: GigRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await request_gig_driver(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/release/{gig_id}", response_model=GigDriverRead)
async def release_gig(gig_id: UUID, db: AsyncSession = Depends(get_db)):
    g = await release_gig_driver(db, gig_id)
    if g is None:
        raise HTTPException(status_code=404, detail="Gig driver not found")
    return g
