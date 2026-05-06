import random
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CreatePlanRequest(BaseModel):
    stops: list[str]


class RoutePlan(BaseModel):
    id: str
    stops: list[str]
    optimized_sequence: list[str]
    total_distance_km: int
    estimated_time_minutes: int
    fuel_cost: int
    created_at: str


class Waypoint(BaseModel):
    lat: float
    lng: float
    name: str


@router.post("/plans")
async def create_plan(req: CreatePlanRequest) -> RoutePlan:
    return RoutePlan(
        id=str(uuid.uuid4()),
        stops=req.stops,
        optimized_sequence=list(reversed(req.stops)),
        total_distance_km=random.randint(50, 500),
        estimated_time_minutes=random.randint(60, 480),
        fuel_cost=random.randint(20, 200),
        created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    )


@router.get("/plans/{plan_id}/map")
async def get_plan_map(plan_id: str) -> list[Waypoint]:
    return [
        Waypoint(lat=40.7128, lng=-74.0060, name="Start"),
        Waypoint(lat=40.7580, lng=-73.9855, name="Midpoint"),
        Waypoint(lat=40.7306, lng=-73.9352, name="End"),
    ]
