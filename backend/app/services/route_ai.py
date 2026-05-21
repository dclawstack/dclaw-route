"""AI Route Copilot service.

Demo-ready stub. Pulls live counts from the DB for context and either:
  - Calls OpenRouter (if OPENROUTER_API_KEY is set), or
  - Returns a keyword-routed canned response.

Per REVISED-PRD.md §9, the copilot must be context-aware and suggest next
actions. RAG and Ollama fallback are deferred to a later iteration.
"""
import os
import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stop import Stop
from app.models.driver import Driver
from app.models.route import Route
from app.models.delivery import Delivery
from app.schemas.ai import ChatMessage, RouteChatResponse, SuggestedAction


SYSTEM_PROMPT = (
    "You are the DClaw Route dispatcher copilot. Help the user manage stops, "
    "drivers, routes, and deliveries. Keep replies under 80 words. When the "
    "user requests an action, suggest the next concrete step they should take."
)


async def _gather_context(db: AsyncSession) -> dict[str, int]:
    stops = (await db.execute(select(func.count()).select_from(Stop))).scalar() or 0
    drivers = (await db.execute(select(func.count()).select_from(Driver))).scalar() or 0
    routes = (await db.execute(select(func.count()).select_from(Route))).scalar() or 0
    pending = (
        await db.execute(
            select(func.count()).select_from(Delivery).where(Delivery.status == "pending")
        )
    ).scalar() or 0
    return {"stops": stops, "drivers": drivers, "routes": routes, "pending_deliveries": pending}


def _infer_action(message: str) -> SuggestedAction:
    m = message.lower()
    if any(k in m for k in ("add stop", "new stop", "create stop")):
        return SuggestedAction(type="create_stop", label="Add a stop", target_path="/stops")
    if any(k in m for k in ("new route", "create route", "plan route")):
        return SuggestedAction(type="create_route", label="Create a route", target_path="/routes")
    if any(k in m for k in ("assign driver", "driver for")):
        return SuggestedAction(
            type="assign_driver", label="Assign a driver", target_path="/routes"
        )
    if any(k in m for k in ("optimize", "reorder", "rearrange")):
        return SuggestedAction(
            type="optimize_route", label="Optimize the current route", target_path="/routes"
        )
    return SuggestedAction(type="none", label="")


def _canned_reply(message: str, ctx: dict[str, int]) -> str:
    action = _infer_action(message)
    base = (
        f"You currently have {ctx['stops']} stops, {ctx['routes']} routes, "
        f"{ctx['drivers']} drivers, and {ctx['pending_deliveries']} pending deliveries."
    )
    if action.type == "none":
        return (
            f"{base} I can help you add stops, plan routes, assign drivers, or optimize "
            "an existing route. What would you like to do?"
        )
    return f"{base} Next step: {action.label.lower()}."


async def _call_openrouter(
    message: str, history: list[ChatMessage], ctx: dict[str, int], api_key: str
) -> str | None:
    model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")
    context_msg = (
        f"Current state: {ctx['stops']} stops, {ctx['routes']} routes, "
        f"{ctx['drivers']} drivers, {ctx['pending_deliveries']} pending deliveries."
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": context_msg},
        *[{"role": m.role, "content": m.content} for m in history],
        {"role": "user", "content": message},
    ]
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": model, "messages": messages, "max_tokens": 200},
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except Exception:
        return None


async def chat(
    db: AsyncSession, message: str, history: list[ChatMessage]
) -> RouteChatResponse:
    ctx = await _gather_context(db)
    action = _infer_action(message)
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()

    if api_key:
        reply = await _call_openrouter(message, history, ctx, api_key)
        if reply:
            return RouteChatResponse(reply=reply, suggested_action=action, provider="openrouter")

    return RouteChatResponse(
        reply=_canned_reply(message, ctx), suggested_action=action, provider="stub"
    )
