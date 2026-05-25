import pytest


@pytest.mark.asyncio
async def test_route_pnl_returns_zero_for_empty_route(client):
    r = await client.post("/api/v1/routes/", json={"name": "Empty"})
    route_id = r.json()["id"]
    res = await client.get(f"/api/v1/analytics/routes/{route_id}/pnl")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["stop_count"] == 0
    assert body["total_cost_usd"] == 0
    assert body["cost_per_delivery"] == 0


@pytest.mark.asyncio
async def test_route_pnl_breakdown(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "A", "lat": 40.0, "lng": -74.0},
    )
    s2 = await client.post(
        "/api/v1/stops/",
        json={"name": "B", "address": "B", "lat": 41.0, "lng": -74.0},
    )
    r = await client.post(
        "/api/v1/routes/",
        json={
            "name": "Test",
            "stop_ids": [s.json()["id"], s2.json()["id"]],
            "total_distance_km": 100.0,
            "estimated_minutes": 120,
        },
    )
    route_id = r.json()["id"]

    res = await client.get(f"/api/v1/analytics/routes/{route_id}/pnl")
    body = res.json()
    # fuel 100 * 0.18 = 18, labor (120/60) * 25 = 50, vehicle 100 * 0.12 = 12 = 80
    assert body["fuel_cost_usd"] == 18.0
    assert body["labor_cost_usd"] == 50.0
    assert body["vehicle_cost_usd"] == 12.0
    assert body["total_cost_usd"] == 80.0
    assert body["miles_per_stop"] == 50.0
    assert body["cost_per_delivery"] == 40.0


@pytest.mark.asyncio
async def test_on_time_rate_after_completion(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "A", "lat": 0.0, "lng": 0.0},
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    delivery_id = r.json()["deliveries"][0]["id"]
    await client.patch(
        f"/api/v1/deliveries/{delivery_id}", json={"status": "completed"}
    )

    res = await client.get(f"/api/v1/analytics/routes/{r.json()['id']}/pnl")
    body = res.json()
    assert body["completed_count"] == 1
    assert body["on_time_rate_pct"] == 100.0


@pytest.mark.asyncio
async def test_fleet_summary_aggregates(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "A", "lat": 0.0, "lng": 0.0},
    )
    await client.post(
        "/api/v1/routes/",
        json={
            "name": "R1",
            "stop_ids": [s.json()["id"]],
            "total_distance_km": 50.0,
            "estimated_minutes": 60,
        },
    )
    await client.post(
        "/api/v1/routes/",
        json={
            "name": "R2",
            "stop_ids": [s.json()["id"]],
            "total_distance_km": 50.0,
            "estimated_minutes": 60,
        },
    )

    res = await client.get("/api/v1/analytics/summary")
    body = res.json()
    assert body["route_count"] == 2
    assert body["total_distance_km"] == 100.0
    assert "fuel_per_km_usd" in body["rates"]


@pytest.mark.asyncio
async def test_pnl_404_for_missing_route(client):
    r = await client.get(
        "/api/v1/analytics/routes/00000000-0000-0000-0000-000000000000/pnl"
    )
    assert r.status_code == 404
