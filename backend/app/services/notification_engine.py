"""Customer notification engine.

Demo-ready stub: renders a template with delivery + stop context and
"sends" by writing a NotificationEvent row. Real impl plugs in Twilio
(SMS) and SendGrid/SES (email) providers.

Templates support `{var}` substitution. Known variables:
  - {customer_name}     — stop.name
  - {address}           — stop.address
  - {route_name}        — route.name
  - {driver_name}       — driver.name (or "your driver")
  - {minutes_away}      — ETA placeholder (defaults to "soon")
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery import Delivery
from app.models.driver import Driver
from app.models.notification import NotificationEvent, NotificationTemplate
from app.models.route import Route
from app.models.stop import Stop


DEFAULT_TEMPLATES: dict[str, tuple[str, str]] = {
    "on_the_way": (
        "Your delivery is on the way",
        "Hi {customer_name}, {driver_name} is heading to {address}. ETA: {minutes_away} min.",
    ),
    "fifteen_minute_warning": (
        "15-minute warning",
        "Hi {customer_name}, your delivery to {address} arrives in about 15 minutes.",
    ),
    "delivered": (
        "Delivered",
        "Hi {customer_name}, your delivery to {address} was completed by {driver_name}. Thank you!",
    ),
}


async def ensure_default_templates(db: AsyncSession) -> None:
    """Idempotent: insert any default templates that are missing."""
    result = await db.execute(select(NotificationTemplate.kind))
    existing = {row[0] for row in result}
    for kind, (subject, body) in DEFAULT_TEMPLATES.items():
        if kind not in existing:
            db.add(NotificationTemplate(kind=kind, subject=subject, body=body))
    await db.commit()


def _render(template: str, ctx: dict[str, str]) -> str:
    out = template
    for k, v in ctx.items():
        out = out.replace("{" + k + "}", v)
    return out


async def _resolve_context(
    db: AsyncSession, delivery: Delivery
) -> tuple[Stop | None, Route | None, Driver | None]:
    stop_result = await db.execute(select(Stop).where(Stop.id == delivery.stop_id))
    stop = stop_result.scalar_one_or_none()
    route_result = await db.execute(select(Route).where(Route.id == delivery.route_id))
    route = route_result.scalar_one_or_none()
    driver: Driver | None = None
    if route and route.driver_id:
        driver_result = await db.execute(
            select(Driver).where(Driver.id == route.driver_id)
        )
        driver = driver_result.scalar_one_or_none()
    return stop, route, driver


async def send_notification(
    db: AsyncSession,
    delivery_id: UUID,
    kind: str,
    minutes_away: str = "soon",
) -> NotificationEvent | None:
    """Render the template, write a NotificationEvent row. Returns None if no
    matching template or no customer contact info on the stop."""
    delivery_result = await db.execute(
        select(Delivery).where(Delivery.id == delivery_id)
    )
    delivery = delivery_result.scalar_one_or_none()
    if not delivery:
        return None

    tpl_result = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.kind == kind)
    )
    tpl = tpl_result.scalar_one_or_none()
    if not tpl:
        return None

    stop, route, driver = await _resolve_context(db, delivery)
    if not stop:
        return None

    recipient = stop.customer_email or stop.customer_phone
    if not recipient:
        return None
    channel = "email" if stop.customer_email else "sms"

    ctx = {
        "customer_name": stop.name,
        "address": stop.address,
        "route_name": route.name if route else "",
        "driver_name": driver.name if driver else "your driver",
        "minutes_away": minutes_away,
    }
    event = NotificationEvent(
        delivery_id=delivery.id,
        kind=kind,
        channel=channel,
        recipient=recipient,
        subject=_render(tpl.subject, ctx),
        body=_render(tpl.body, ctx),
        status="sent",
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
