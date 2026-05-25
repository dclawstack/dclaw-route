from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class LoadingItem(BaseModel):
    delivery_id: UUID
    stop_id: UUID
    stop_name: str
    load_position: int  # 0 = closest to truck door
    delivery_sequence: int  # original stop order on the route


class LoadingManifest(BaseModel):
    route_id: UUID
    route_name: str
    dock_number: str | None
    item_count: int
    items: list[LoadingItem]


class DockAssignment(BaseModel):
    route_id: UUID
    dock_number: str


class WmsSyncResult(BaseModel):
    routes_synced: int
    deliveries_synced: int
    timestamp: datetime
