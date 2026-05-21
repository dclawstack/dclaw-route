from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route import Route
from app.repositories.base_repo import BaseRepository


class RouteRepository(BaseRepository[Route]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Route)
