from sqlalchemy.ext.asyncio import AsyncSession

from app.models.driver_shift import DriverShift
from app.repositories.base_repo import BaseRepository


class DriverShiftRepository(BaseRepository[DriverShift]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DriverShift)
