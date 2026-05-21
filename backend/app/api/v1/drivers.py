from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.driver import Driver
from app.repositories.driver_repo import DriverRepository
from app.schemas.driver import DriverCreate, DriverRead, DriverUpdate

router = APIRouter()


@router.get("/", response_model=list[DriverRead])
async def list_drivers(limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)):
    repo = DriverRepository(db)
    items, _ = await repo.list_all(limit=limit, offset=offset)
    return items


@router.post("/", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
async def create_driver(payload: DriverCreate, db: AsyncSession = Depends(get_db)):
    repo = DriverRepository(db)
    driver = Driver(**payload.model_dump())
    return await repo.create(driver)


@router.get("/{driver_id}", response_model=DriverRead)
async def get_driver(driver_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = DriverRepository(db)
    driver = await repo.get_by_id(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.patch("/{driver_id}", response_model=DriverRead)
async def update_driver(driver_id: UUID, payload: DriverUpdate, db: AsyncSession = Depends(get_db)):
    repo = DriverRepository(db)
    driver = await repo.get_by_id(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(driver, k, v)
    await db.commit()
    await db.refresh(driver)
    return driver


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(driver_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = DriverRepository(db)
    driver = await repo.get_by_id(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    await repo.delete(driver)
