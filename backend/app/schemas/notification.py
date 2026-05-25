from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TemplateBase(BaseModel):
    kind: str
    subject: str
    body: str


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    subject: str | None = None
    body: str | None = None


class TemplateRead(TemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationEventRead(BaseModel):
    id: UUID
    delivery_id: UUID | None
    kind: str
    channel: str
    recipient: str
    subject: str
    body: str
    status: str
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ManualSendRequest(BaseModel):
    delivery_id: UUID
    kind: str  # "on_the_way" | "fifteen_minute_warning" | "delivered" | custom
