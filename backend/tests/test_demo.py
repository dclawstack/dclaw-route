import pytest


@pytest.mark.asyncio
async def test_demo_status_starts_empty(client):
    r = await client.get("/api/v1/demo/status")
    assert r.status_code == 200
    body = r.json()
    assert body["enabled"] is True
    assert body["seeded"] is False
    assert body["stop_count"] == 0


@pytest.mark.asyncio
async def test_seed_populates_stops_drivers_vehicles_routes(client):
    r = await client.post("/api/v1/demo/seed")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["seeded"] is True
    assert body["stop_count"] >= 8
    assert body["driver_count"] >= 3
    assert body["vehicle_count"] >= 3
    assert body["route_count"] >= 2

    # All demo names are properly prefixed.
    stops = (await client.get("/api/v1/stops/")).json()
    assert all(s["name"].startswith("DEMO ") for s in stops)


@pytest.mark.asyncio
async def test_seed_is_idempotent(client):
    a = await client.post("/api/v1/demo/seed")
    b = await client.post("/api/v1/demo/seed")
    assert a.json()["stop_count"] == b.json()["stop_count"]
    assert a.json()["route_count"] == b.json()["route_count"]


@pytest.mark.asyncio
async def test_reset_only_clears_demo_rows(client):
    # A non-demo row that should survive.
    real = await client.post(
        "/api/v1/stops/",
        json={"name": "Real customer", "address": "X", "lat": 0.0, "lng": 0.0},
    )

    await client.post("/api/v1/demo/seed")
    await client.delete("/api/v1/demo/reset")

    status_after = (await client.get("/api/v1/demo/status")).json()
    assert status_after["seeded"] is False
    assert status_after["stop_count"] == 0

    stops_after = (await client.get("/api/v1/stops/")).json()
    assert any(s["id"] == real.json()["id"] for s in stops_after)
    assert all(not s["name"].startswith("DEMO ") for s in stops_after)


@pytest.mark.asyncio
async def test_seeded_routes_have_deliveries(client):
    await client.post("/api/v1/demo/seed")
    routes = (await client.get("/api/v1/routes/")).json()
    demo_routes = [r for r in routes if r["name"].startswith("DEMO ")]
    assert len(demo_routes) == 2
    assert all(len(r["deliveries"]) >= 3 for r in demo_routes)
