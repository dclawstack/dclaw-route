from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.notification import NotificationEvent, NotificationTemplate
from app.schemas.notification import (
    ManualSendRequest,
    NotificationEventRead,
    TemplateCreate,
    TemplateRead,
    TemplateUpdate,
)
from app.services.notification_engine import (
    ensure_default_templates,
    send_notification,
)

router = APIRouter()


@router.get("/templates", response_model=list[TemplateRead])
async def list_templates(db: AsyncSession = Depends(get_db)):
    await ensure_default_templates(db)
    result = await db.execute(select(NotificationTemplate))
    return list(result.scalars().all())


@router.post("/templates", response_model=TemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(payload: TemplateCreate, db: AsyncSession = Depends(get_db)):
    tpl = NotificationTemplate(**payload.model_dump())
    db.add(tpl)
    await db.commit()
    await db.refresh(tpl)
    return tpl


@router.patch("/templates/{template_id}", response_model=TemplateRead)
async def update_template(
    template_id: UUID, payload: TemplateUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.id == template_id)
    )
    tpl = result.scalar_one_or_none()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(tpl, k, v)
    await db.commit()
    await db.refresh(tpl)
    return tpl


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.id == template_id)
    )
    tpl = result.scalar_one_or_none()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.delete(tpl)
    await db.commit()


@router.get("/events", response_model=list[NotificationEventRead])
async def list_events(
    delivery_id: UUID | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(NotificationEvent)
    if delivery_id is not None:
        stmt = stmt.where(NotificationEvent.delivery_id == delivery_id)
    stmt = stmt.order_by(NotificationEvent.sent_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/send", response_model=NotificationEventRead)
async def manual_send(payload: ManualSendRequest, db: AsyncSession = Depends(get_db)):
    await ensure_default_templates(db)
    event = await send_notification(db, payload.delivery_id, payload.kind)
    if event is None:
        raise HTTPException(
            status_code=400,
            detail="Cannot send — check delivery, template, or customer contact info",
        )
    return event
