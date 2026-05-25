import pytest


@pytest.mark.asyncio
async def test_request_return_creates_pickup_on_queue(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "A", "lat": 1.0, "lng": 1.0},
    )
    r = await client.post(
        "/api/v1/returns/request",
        json={"stop_id": s.json()["id"], "notes": "wrong size"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kind"] == "pickup"
    assert body["status"] == "pending"
    assert body["notes"] == "wrong size"

    pending = await client.get("/api/v1/returns/pending")
    assert len(pending.json()) == 1


@pytest.mark.asyncio
async def test_pending_empty_when_no_requests(client):
    r = await client.get("/api/v1/returns/pending")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_consolidate_returns_into_new_route(client):
    # Create 3 stops in a deliberately bad-NN order.
    coords = [(40.7, -74.0), (37.7, -122.4), (40.75, -74.0)]
    stop_ids = []
    for i, (lat, lng) in enumerate(coords):
        s = await client.post(
            "/api/v1/stops/",
            json={"name": f"S{i}", "address": str(i), "lat": lat, "lng": lng},
        )
        stop_ids.append(s.json()["id"])

    for sid in stop_ids:
        await client.post("/api/v1/returns/request", json={"stop_id": sid})

    r = await client.post("/api/v1/returns/consolidate")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["consolidated_count"] == 3
    assert "Return run" in body["route_name"]
    assert body["total_distance_km"] > 0

    # Queue should be empty after consolidation.
    pending = await client.get("/api/v1/returns/pending")
    assert pending.json() == []

    # The new route should hold the 3 pickups.
    new_route = await client.get(f"/api/v1/routes/{body['route_id']}")
    assert len(new_route.json()["deliveries"]) == 3
    assert all(d["kind"] == "pickup" for d in new_route.json()["deliveries"])


@pytest.mark.asyncio
async def test_consolidate_rejects_with_fewer_than_2(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "A", "lat": 1.0, "lng": 1.0},
    )
    await client.post("/api/v1/returns/request", json={"stop_id": s.json()["id"]})
    r = await client.post("/api/v1/returns/consolidate")
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_regular_delivery_kind_defaults_to_drop_off(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "A", "lat": 1.0, "lng": 1.0},
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    assert r.json()["deliveries"][0]["kind"] == "drop_off"
