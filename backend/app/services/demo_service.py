"""Public demo dataset service.

Powers the /api/v1/demo/* endpoints the landing page uses to give a
logged-out visitor a working dataset to click through.

Identification:
- Every demo row is named with the prefix ``DEMO `` so they can be
  found and removed safely.
- reset_demo() only deletes rows that match these markers, so it can
  never touch real data even if the feature flag is on by mistake.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import utc_now
from app.models.delivery import Delivery
from app.models.driver import Driver
from app.models.route import Route
from app.models.stop import Stop
from app.models.vehicle import Vehicle


DEMO_PREFIX = "DEMO "


@dataclass
class DemoStatus:
    enabled: bool
    seeded: bool
    stop_count: int
    driver_count: int
    vehicle_count: int
    route_count: int


_DEMO_STOPS: list[dict] = [
    {"name": "Warehouse A", "address": "1 Industrial Way, Brooklyn NY", "lat": 40.6928, "lng": -73.9903, "customer_email": "warehouse@example.com"},
    {"name": "Customer · Tribeca", "address": "100 Hudson St, NY", "lat": 40.7195, "lng": -74.0085, "customer_email": "tribeca@example.com"},
    {"name": "Customer · Midtown", "address": "350 5th Ave, NY", "lat": 40.7484, "lng": -73.9857, "customer_email": "midtown@example.com"},
    {"name": "Customer · UWS", "address": "200 W 86th St, NY", "lat": 40.7873, "lng": -73.9756, "customer_phone": "+15550100001"},
    {"name": "Customer · Harlem", "address": "125th & Lenox, NY", "lat": 40.8074, "lng": -73.9456, "customer_phone": "+15550100002"},
    {"name": "Customer · LIC", "address": "44-02 23rd St, Queens", "lat": 40.7510, "lng": -73.9418, "customer_email": "lic@example.com"},
    {"name": "Customer · DUMBO", "address": "1 Front St, Brooklyn", "lat": 40.7029, "lng": -73.9890, "customer_email": "dumbo@example.com"},
    {"name": "Customer · Park Slope", "address": "200 7th Ave, Brooklyn", "lat": 40.6712, "lng": -73.9778, "customer_phone": "+15550100003"},
]

_DEMO_DRIVERS: list[dict] = [
    {"name": "DEMO Alice Chen", "email": "demo.alice@example.com", "vehicle_type": "van"},
    {"name": "DEMO Bob Martinez", "email": "demo.bob@example.com", "vehicle_type": "truck"},
    {"name": "DEMO Carla Singh", "email": "demo.carla@example.com", "vehicle_type": "bike"},
]

_DEMO_VEHICLES: list[dict] = [
    {"plate": "DEMO-EV1", "vehicle_type": "van", "capacity_kg": 1200.0, "odometer_km": 23000, "co2_g_per_km": 60.0},
    {"plate": "DEMO-TRK", "vehicle_type": "truck", "capacity_kg": 3500.0, "odometer_km": 87000, "co2_g_per_km": 750.0},
    {"plate": "DEMO-BIK", "vehicle_type": "bike", "capacity_kg": 50.0, "odometer_km": 4200, "co2_g_per_km": 0.0},
]


async def get_demo_status(db: AsyncSession, *, enabled: bool) -> DemoStatus:
    return DemoStatus(
        enabled=enabled,
        seeded=(await _count_demo(db, Stop, Stop.name)) > 0,
        stop_count=await _count_demo(db, Stop, Stop.name),
        driver_count=await _count_demo(db, Driver, Driver.name),
        vehicle_count=await _count_demo(db, Vehicle, Vehicle.plate),
        route_count=await _count_demo(db, Route, Route.name),
    )


async def seed_demo(db: AsyncSession) -> DemoStatus:
    """Create the demo dataset. Idempotent — re-running adds nothing new."""
    existing_stops = await _existing_names(db, Stop, Stop.name)
    stop_ids_by_name: dict[str, object] = {}
    for spec in _DEMO_STOPS:
        demo_name = DEMO_PREFIX + spec["name"]
        if demo_name in existing_stops:
            # Look it up to wire to routes.
            result = await db.execute(select(Stop).where(Stop.name == demo_name))
            existing = result.scalar_one_or_none()
            if existing:
                stop_ids_by_name[demo_name] = existing.id
            continue
        stop = Stop(name=demo_name, **{k: v for k, v in spec.items() if k != "name"})
        db.add(stop)
        await db.flush()
        stop_ids_by_name[demo_name] = stop.id

    existing_drivers = await _existing_names(db, Driver, Driver.name)
    driver_ids: list[object] = []
    for spec in _DEMO_DRIVERS:
        if spec["name"] in existing_drivers:
            result = await db.execute(select(Driver).where(Driver.name == spec["name"]))
            existing = result.scalar_one_or_none()
            if existing:
                driver_ids.append(existing.id)
            continue
        d = Driver(**spec)
        db.add(d)
        await db.flush()
        driver_ids.append(d.id)

    existing_vehicles = await _existing_names(db, Vehicle, Vehicle.plate)
    vehicle_ids: list[object] = []
    for spec in _DEMO_VEHICLES:
        if spec["plate"] in existing_vehicles:
            result = await db.execute(select(Vehicle).where(Vehicle.plate == spec["plate"]))
            existing = result.scalar_one_or_none()
            if existing:
                vehicle_ids.append(existing.id)
            continue
        v = Vehicle(**spec)
        db.add(v)
        await db.flush()
        vehicle_ids.append(v.id)

    # Two routes: morning loop (4 customers) and afternoon loop (3 customers).
    morning_name = f"{DEMO_PREFIX}Morning loop"
    afternoon_name = f"{DEMO_PREFIX}Afternoon loop"
    existing_routes = await _existing_names(db, Route, Route.name)

    if morning_name not in existing_routes:
        morning_stops = [
            stop_ids_by_name[f"{DEMO_PREFIX}Customer · Tribeca"],
            stop_ids_by_name[f"{DEMO_PREFIX}Customer · Midtown"],
            stop_ids_by_name[f"{DEMO_PREFIX}Customer · UWS"],
            stop_ids_by_name[f"{DEMO_PREFIX}Customer · Harlem"],
        ]
        route = Route(
            name=morning_name,
            driver_id=driver_ids[0] if driver_ids else None,
            vehicle_id=vehicle_ids[0] if vehicle_ids else None,
            status="planned",
            total_distance_km=24.6,
            estimated_minutes=72,
        )
        db.add(route)
        await db.flush()
        for i, sid in enumerate(morning_stops):
            db.add(Delivery(route_id=route.id, stop_id=sid, sequence=i))

    if afternoon_name not in existing_routes:
        afternoon_stops = [
            stop_ids_by_name[f"{DEMO_PREFIX}Customer · LIC"],
            stop_ids_by_name[f"{DEMO_PREFIX}Customer · DUMBO"],
            stop_ids_by_name[f"{DEMO_PREFIX}Customer · Park Slope"],
        ]
        route = Route(
            name=afternoon_name,
            driver_id=driver_ids[1] if len(driver_ids) > 1 else None,
            vehicle_id=vehicle_ids[1] if len(vehicle_ids) > 1 else None,
            status="planned",
            total_distance_km=18.3,
            estimated_minutes=55,
        )
        db.add(route)
        await db.flush()
        for i, sid in enumerate(afternoon_stops):
            db.add(Delivery(route_id=route.id, stop_id=sid, sequence=i))

    # Park the bike driver near downtown for live-tracking demo.
    if len(driver_ids) >= 3:
        await db.execute(
            select(Driver).where(Driver.id == driver_ids[2])
        )
        result = await db.execute(select(Driver).where(Driver.id == driver_ids[2]))
        biker = result.scalar_one_or_none()
        if biker and biker.current_lat is None:
            biker.current_lat = 40.7128
            biker.current_lng = -74.0060
            biker.location_updated_at = utc_now()

    await db.commit()
    return await get_demo_status(db, enabled=True)


async def reset_demo(db: AsyncSession) -> DemoStatus:
    """Delete every DEMO-prefixed row. Cascades take care of deliveries."""
    await db.execute(delete(Route).where(Route.name.startswith(DEMO_PREFIX)))
    await db.execute(delete(Stop).where(Stop.name.startswith(DEMO_PREFIX)))
    await db.execute(delete(Driver).where(Driver.name.startswith(DEMO_PREFIX)))
    await db.execute(
        delete(Vehicle).where(Vehicle.plate.startswith("DEMO-"))
    )
    await db.commit()
    return await get_demo_status(db, enabled=True)


async def _count_demo(db: AsyncSession, model, column) -> int:
    prefix = "DEMO-" if column.key == "plate" else DEMO_PREFIX
    res = await db.execute(
        select(func.count()).select_from(model).where(column.startswith(prefix))
    )
    return int(res.scalar() or 0)


async def _existing_names(db: AsyncSession, model, column) -> set[str]:
    prefix = "DEMO-" if column.key == "plate" else DEMO_PREFIX
    res = await db.execute(select(column).where(column.startswith(prefix)))
    return {row[0] for row in res.all()}
