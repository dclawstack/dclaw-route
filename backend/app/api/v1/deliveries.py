from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.utils import utc_now
from app.models.delivery import Delivery
from app.repositories.delivery_repo import DeliveryRepository
from app.schemas.delivery import DeliveryCreate, DeliveryRead, DeliveryUpdate

router = APIRouter()


@router.get("/", response_model=list[DeliveryRead])
async def list_deliveries(
    route_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Delivery)
    if route_id is not None:
        stmt = stmt.where(Delivery.route_id == route_id)
    stmt = stmt.order_by(Delivery.sequence).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=DeliveryRead, status_code=status.HTTP_201_CREATED)
async def create_delivery(payload: DeliveryCreate, db: AsyncSession = Depends(get_db)):
    repo = DeliveryRepository(db)
    delivery = Delivery(**payload.model_dump())
    return await repo.create(delivery)


@router.get("/{delivery_id}", response_model=DeliveryRead)
async def get_delivery(delivery_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = DeliveryRepository(db)
    delivery = await repo.get_by_id(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.patch("/{delivery_id}", response_model=DeliveryRead)
async def update_delivery(
    delivery_id: UUID, payload: DeliveryUpdate, db: AsyncSession = Depends(get_db)
):
    repo = DeliveryRepository(db)
    delivery = await repo.get_by_id(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    data = payload.model_dump(exclude_unset=True)
    if data.get("status") == "completed" and delivery.completed_at is None:
        delivery.completed_at = utc_now()
    for k, v in data.items():
        setattr(delivery, k, v)
    await db.commit()
    await db.refresh(delivery)
    return delivery


@router.delete("/{delivery_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_delivery(delivery_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = DeliveryRepository(db)
    delivery = await repo.get_by_id(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    await repo.delete(delivery)
