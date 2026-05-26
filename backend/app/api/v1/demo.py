"""Public demo dataset endpoints.

Gated by settings.enable_demo_mode. When off, every endpoint returns 403
so production deploys can flip the flag to disable the surface.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.demo_service import get_demo_status, reset_demo, seed_demo

router = APIRouter()


class DemoStatusResponse(BaseModel):
    enabled: bool
    seeded: bool
    stop_count: int
    driver_count: int
    vehicle_count: int
    route_count: int

    model_config = ConfigDict(from_attributes=True)


def _require_enabled() -> None:
    if not settings.enable_demo_mode:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo mode is disabled (set ENABLE_DEMO_MODE=true).",
        )


@router.get("/status", response_model=DemoStatusResponse)
async def status_endpoint(db: AsyncSession = Depends(get_db)) -> DemoStatusResponse:
    s = await get_demo_status(db, enabled=settings.enable_demo_mode)
    return DemoStatusResponse(**s.__dict__)


@router.post("/seed", response_model=DemoStatusResponse)
async def seed_endpoint(db: AsyncSession = Depends(get_db)) -> DemoStatusResponse:
    _require_enabled()
    s = await seed_demo(db)
    return DemoStatusResponse(**s.__dict__)


@router.delete("/reset", response_model=DemoStatusResponse)
async def reset_endpoint(db: AsyncSession = Depends(get_db)) -> DemoStatusResponse:
    _require_enabled()
    s = await reset_demo(db)
    return DemoStatusResponse(**s.__dict__)
