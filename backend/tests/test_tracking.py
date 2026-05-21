import pytest


@pytest.mark.asyncio
async def test_update_driver_location(client):
    d = await client.post(
        "/api/v1/drivers/", json={"name": "Eve", "email": "e@example.com"}
    )
    driver_id = d.json()["id"]
    r = await client.post(
        f"/api/v1/tracking/drivers/{driver_id}/location",
        json={"lat": 40.7128, "lng": -74.0060},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["current_lat"] == 40.7128
    assert body["current_lng"] == -74.0060
    assert body["location_updated_at"] is not None

    # Verify driver record persists the location.
    g = await client.get(f"/api/v1/drivers/{driver_id}")
    assert g.json()["current_lat"] == 40.7128


@pytest.mark.asyncio
async def test_route_eta_includes_each_pending_stop(client):
    d = await client.post(
        "/api/v1/drivers/", json={"name": "Frank", "email": "f@example.com"}
    )
    driver_id = d.json()["id"]
    s1 = await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "A", "lat": 40.7128, "lng": -74.0060},
    )
    s2 = await client.post(
        "/api/v1/stops/",
        json={"name": "B", "address": "B", "lat": 40.7580, "lng": -73.9855},
    )

    r = await client.post(
        "/api/v1/routes/",
        json={
            "name": "R",
            "driver_id": driver_id,
            "stop_ids": [s1.json()["id"], s2.json()["id"]],
        },
    )
    route_id = r.json()["id"]

    # Ping driver position near stop A.
    await client.post(
        f"/api/v1/tracking/drivers/{driver_id}/location",
        json={"lat": 40.7128, "lng": -74.0060},
    )

    eta = await client.get(f"/api/v1/tracking/routes/{route_id}/eta")
    assert eta.status_code == 200, eta.text
    body = eta.json()
    assert len(body["stops"]) == 2
    assert body["stops"][0]["cumulative_km"] >= 0
    assert body["stops"][1]["cumulative_km"] > body["stops"][0]["cumulative_km"]
    assert body["driver_position"] == [40.7128, -74.0060]
    assert body["is_delayed"] is False


@pytest.mark.asyncio
async def test_route_eta_skips_completed_deliveries(client):
    s1 = await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "A", "lat": 40.0, "lng": -74.0},
    )
    s2 = await client.post(
        "/api/v1/stops/",
        json={"name": "B", "address": "B", "lat": 41.0, "lng": -74.0},
    )
    r = await client.post(
        "/api/v1/routes/",
        json={"name": "R", "stop_ids": [s1.json()["id"], s2.json()["id"]]},
    )
    delivery_id = r.json()["deliveries"][0]["id"]
    await client.patch(
        f"/api/v1/deliveries/{delivery_id}", json={"status": "completed"}
    )

    eta = await client.get(f"/api/v1/tracking/routes/{r.json()['id']}/eta")
    assert len(eta.json()["stops"]) == 1
    assert eta.json()["stops"][0]["stop_name"] == "B"


@pytest.mark.asyncio
async def test_eta_404_for_missing_route(client):
    r = await client.get(
        "/api/v1/tracking/routes/00000000-0000-0000-0000-000000000000/eta"
    )
    assert r.status_code == 404
