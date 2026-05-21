from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.stop import Stop
from app.repositories.stop_repo import StopRepository
from app.schemas.stop import StopCreate, StopRead, StopUpdate

router = APIRouter()


@router.get("/", response_model=list[StopRead])
async def list_stops(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    repo = StopRepository(db)
    items, _ = await repo.list_all(limit=limit, offset=offset)
    return items


@router.post("/", response_model=StopRead, status_code=status.HTTP_201_CREATED)
async def create_stop(payload: StopCreate, db: AsyncSession = Depends(get_db)):
    repo = StopRepository(db)
    stop = Stop(**payload.model_dump())
    return await repo.create(stop)


@router.get("/{stop_id}", response_model=StopRead)
async def get_stop(stop_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = StopRepository(db)
    stop = await repo.get_by_id(stop_id)
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    return stop


@router.patch("/{stop_id}", response_model=StopRead)
async def update_stop(stop_id: UUID, payload: StopUpdate, db: AsyncSession = Depends(get_db)):
    repo = StopRepository(db)
    stop = await repo.get_by_id(stop_id)
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(stop, k, v)
    await db.commit()
    await db.refresh(stop)
    return stop


@router.delete("/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stop(stop_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = StopRepository(db)
    stop = await repo.get_by_id(stop_id)
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
    await repo.delete(stop)
