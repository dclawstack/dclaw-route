from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.territory import Territory
from app.schemas.territory import (
    ClusterRequest,
    ClusterResult,
    TerritoryCreate,
    TerritoryRead,
    TerritoryUpdate,
)
from app.services.territory_planner import cluster_stops

router = APIRouter()


@router.get("/", response_model=list[TerritoryRead])
async def list_territories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Territory))
    return list(result.scalars().all())


@router.post("/", response_model=TerritoryRead, status_code=status.HTTP_201_CREATED)
async def create_territory(payload: TerritoryCreate, db: AsyncSession = Depends(get_db)):
    t = Territory(**payload.model_dump())
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t


@router.patch("/{territory_id}", response_model=TerritoryRead)
async def update_territory(
    territory_id: UUID, payload: TerritoryUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Territory).where(Territory.id == territory_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Territory not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    await db.commit()
    await db.refresh(t)
    return t


@router.delete("/{territory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_territory(territory_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Territory).where(Territory.id == territory_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Territory not found")
    await db.delete(t)
    await db.commit()


@router.post("/cluster", response_model=ClusterResult)
async def cluster(payload: ClusterRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await cluster_stops(db, payload.n, payload.max_iterations)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
