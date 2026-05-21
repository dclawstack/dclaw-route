"""HOS (Hours-of-Service) fatigue monitor.

Demo-ready stub of the FMCSA 60/70-hour rule: max 60 hours over any
rolling 7-day period. Severity tiers:
  - ok       : < 50 h
  - warning  : 50–60 h
  - critical : >= 60 h
"""
from datetime import timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import utc_now
from app.models.driver import Driver
from app.models.driver_shift import DriverShift
from app.schemas.driver_shift import FatigueAlert


HOS_LIMIT_HOURS = 60.0
WARNING_THRESHOLD = 50.0
WINDOW_DAYS = 7


def _severity(hours: float) -> str:
    if hours >= HOS_LIMIT_HOURS:
        return "critical"
    if hours >= WARNING_THRESHOLD:
        return "warning"
    return "ok"


async def alerts_for_all_drivers(db: AsyncSession) -> list[FatigueAlert]:
    cutoff = utc_now() - timedelta(days=WINDOW_DAYS)
    drivers_result = await db.execute(select(Driver))
    out: list[FatigueAlert] = []
    for driver in drivers_result.scalars():
        shifts_result = await db.execute(
            select(DriverShift).where(
                DriverShift.driver_id == driver.id, DriverShift.start_at >= cutoff
            )
        )
        hours = sum(s.hours_worked for s in shifts_result.scalars())
        out.append(
            FatigueAlert(
                driver_id=driver.id,
                driver_name=driver.name,
                hours_last_7_days=round(hours, 2),
                limit_hours=HOS_LIMIT_HOURS,
                remaining_hours=round(max(0.0, HOS_LIMIT_HOURS - hours), 2),
                severity=_severity(hours),
            )
        )
    return out


async def alert_for_driver(db: AsyncSession, driver_id: UUID) -> FatigueAlert | None:
    driver_result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = driver_result.scalar_one_or_none()
    if driver is None:
        return None
    cutoff = utc_now() - timedelta(days=WINDOW_DAYS)
    shifts_result = await db.execute(
        select(DriverShift).where(
            DriverShift.driver_id == driver_id, DriverShift.start_at >= cutoff
        )
    )
    hours = sum(s.hours_worked for s in shifts_result.scalars())
    return FatigueAlert(
        driver_id=driver.id,
        driver_name=driver.name,
        hours_last_7_days=round(hours, 2),
        limit_hours=HOS_LIMIT_HOURS,
        remaining_hours=round(max(0.0, HOS_LIMIT_HOURS - hours), 2),
        severity=_severity(hours),
    )
