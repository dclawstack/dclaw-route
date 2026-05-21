from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stop import Stop
from app.repositories.base_repo import BaseRepository


class StopRepository(BaseRepository[Stop]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Stop)
