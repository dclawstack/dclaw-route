import pytest


@pytest.mark.asyncio
async def test_create_route_with_stops(client):
    s1 = await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "1", "lat": 1.0, "lng": 1.0},
    )
    s2 = await client.post(
        "/api/v1/stops/",
        json={"name": "B", "address": "2", "lat": 2.0, "lng": 2.0},
    )
    stop_ids = [s1.json()["id"], s2.json()["id"]]

    r = await client.post(
        "/api/v1/routes/",
        json={"name": "Morning run", "stop_ids": stop_ids},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["name"] == "Morning run"
    assert len(body["deliveries"]) == 2
    assert body["deliveries"][0]["sequence"] == 0
    assert body["deliveries"][1]["sequence"] == 1


@pytest.mark.asyncio
async def test_assign_driver_to_route(client):
    d = await client.post(
        "/api/v1/drivers/",
        json={"name": "Carla", "email": "c@example.com"},
    )
    driver_id = d.json()["id"]

    r = await client.post("/api/v1/routes/", json={"name": "R1"})
    route_id = r.json()["id"]

    r2 = await client.patch(f"/api/v1/routes/{route_id}", json={"driver_id": driver_id})
    assert r2.status_code == 200
    assert r2.json()["driver_id"] == driver_id


@pytest.mark.asyncio
async def test_complete_delivery_sets_timestamp(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "X", "address": "X", "lat": 0.0, "lng": 0.0},
    )
    r = await client.post(
        "/api/v1/routes/",
        json={"name": "R", "stop_ids": [s.json()["id"]]},
    )
    delivery_id = r.json()["deliveries"][0]["id"]

    r2 = await client.patch(
        f"/api/v1/deliveries/{delivery_id}", json={"status": "completed"}
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "completed"
    assert r2.json()["completed_at"] is not None
