from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery import Delivery
from app.repositories.base_repo import BaseRepository


class DeliveryRepository(BaseRepository[Delivery]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Delivery)
