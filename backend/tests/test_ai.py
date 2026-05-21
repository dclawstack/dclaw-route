import os
import pytest


@pytest.fixture(autouse=True)
def _no_openrouter_key(monkeypatch):
    """Force the stub path so tests don't hit OpenRouter."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "")


@pytest.mark.asyncio
async def test_route_chat_returns_stub_reply(client):
    r = await client.post(
        "/api/v1/ai/route-chat", json={"message": "hello", "history": []}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["provider"] == "stub"
    assert "0 stops" in body["reply"]
    assert body["suggested_action"]["type"] == "none"


@pytest.mark.asyncio
async def test_route_chat_infers_create_stop_action(client):
    r = await client.post(
        "/api/v1/ai/route-chat",
        json={"message": "I need to add a new stop downtown", "history": []},
    )
    body = r.json()
    assert body["suggested_action"]["type"] == "create_stop"
    assert body["suggested_action"]["target_path"] == "/stops"


@pytest.mark.asyncio
async def test_route_chat_uses_live_context(client):
    await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "1", "lat": 1.0, "lng": 1.0},
    )
    r = await client.post(
        "/api/v1/ai/route-chat", json={"message": "status", "history": []}
    )
    assert "1 stops" in r.json()["reply"]


@pytest.mark.asyncio
async def test_route_chat_infers_optimize_action(client):
    r = await client.post(
        "/api/v1/ai/route-chat",
        json={"message": "Please optimize the morning route", "history": []},
    )
    assert r.json()["suggested_action"]["type"] == "optimize_route"
