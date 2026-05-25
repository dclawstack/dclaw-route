from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.wms import DockAssignment, LoadingManifest, WmsSyncResult
from app.services.wms_sync import assign_dock, loading_manifest, sync_with_wms

router = APIRouter()


class DockAssignmentPayload(BaseModel):
    dock_number: str


@router.get("/routes/{route_id}/loading-sequence", response_model=LoadingManifest)
async def get_loading_sequence(route_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await loading_manifest(db, route_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/routes/{route_id}/dock", response_model=DockAssignment)
async def post_dock_assignment(
    route_id: UUID,
    payload: DockAssignmentPayload,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await assign_dock(db, route_id, payload.dock_number)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sync", response_model=WmsSyncResult)
async def sync(db: AsyncSession = Depends(get_db)):
    return await sync_with_wms(db)
