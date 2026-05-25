import pytest


@pytest.mark.asyncio
async def test_insert_urgent_picks_cheapest_position(client):
    # Route along a north-south line: S1 (south), S2 (mid-north).
    # Urgent stop is just south of S2 — should be inserted between them, not at the end.
    s1 = await client.post(
        "/api/v1/stops/",
        json={"name": "S1", "address": "1", "lat": 40.0, "lng": -74.0},
    )
    s2 = await client.post(
        "/api/v1/stops/",
        json={"name": "S2", "address": "2", "lat": 41.0, "lng": -74.0},
    )
    urgent = await client.post(
        "/api/v1/stops/",
        json={"name": "Urgent", "address": "U", "lat": 40.8, "lng": -73.9},
    )

    r = await client.post(
        "/api/v1/routes/",
        json={"name": "R", "stop_ids": [s1.json()["id"], s2.json()["id"]]},
    )
    route_id = r.json()["id"]

    res = await client.post(
        f"/api/v1/routes/{route_id}/insert-urgent",
        json={"stop_id": urgent.json()["id"]},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["inserted_at_position"] == 1
    assert body["extra_distance_km"] >= 0
    assert body["extra_minutes"] >= 0
    # S2 was shifted to position 2.
    shifted_names = {s["stop_name"]: s for s in body["shifted_stops"]}
    assert "S2" in shifted_names
    assert shifted_names["S2"]["new_sequence"] == 2

    # The route now has 3 deliveries in [S1, Urgent, S2] order.
    route = await client.get(f"/api/v1/routes/{route_id}")
    deliveries = route.json()["deliveries"]
    assert [d["sequence"] for d in deliveries] == [0, 1, 2]


@pytest.mark.asyncio
async def test_insert_urgent_appends_when_cheapest(client):
    # Route at (40, -74) and (41, -74). Urgent way further north.
    # Cheapest is to append.
    s1 = await client.post(
        "/api/v1/stops/",
        json={"name": "S1", "address": "1", "lat": 40.0, "lng": -74.0},
    )
    s2 = await client.post(
        "/api/v1/stops/",
        json={"name": "S2", "address": "2", "lat": 41.0, "lng": -74.0},
    )
    urgent = await client.post(
        "/api/v1/stops/",
        json={"name": "Urgent", "address": "U", "lat": 42.0, "lng": -74.0},
    )

    r = await client.post(
        "/api/v1/routes/",
        json={"name": "R", "stop_ids": [s1.json()["id"], s2.json()["id"]]},
    )
    res = await client.post(
        f"/api/v1/routes/{r.json()['id']}/insert-urgent",
        json={"stop_id": urgent.json()["id"]},
    )
    body = res.json()
    assert body["inserted_at_position"] == 2  # append
    assert body["shifted_stops"] == []


@pytest.mark.asyncio
async def test_insert_urgent_into_empty_route(client):
    urgent = await client.post(
        "/api/v1/stops/",
        json={"name": "U", "address": "U", "lat": 40.0, "lng": -74.0},
    )
    r = await client.post("/api/v1/routes/", json={"name": "Empty"})

    res = await client.post(
        f"/api/v1/routes/{r.json()['id']}/insert-urgent",
        json={"stop_id": urgent.json()["id"]},
    )
    assert res.status_code == 200, res.text
    assert res.json()["inserted_at_position"] == 0
    assert res.json()["extra_distance_km"] == 0


@pytest.mark.asyncio
async def test_insert_urgent_404s_for_missing_route(client):
    stop = await client.post(
        "/api/v1/stops/",
        json={"name": "U", "address": "U", "lat": 1.0, "lng": 1.0},
    )
    r = await client.post(
        "/api/v1/routes/00000000-0000-0000-0000-000000000000/insert-urgent",
        json={"stop_id": stop.json()["id"]},
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_insert_urgent_skips_completed_stops(client):
    s1 = await client.post(
        "/api/v1/stops/",
        json={"name": "S1", "address": "1", "lat": 40.0, "lng": -74.0},
    )
    s2 = await client.post(
        "/api/v1/stops/",
        json={"name": "S2", "address": "2", "lat": 41.0, "lng": -74.0},
    )
    r = await client.post(
        "/api/v1/routes/",
        json={"name": "R", "stop_ids": [s1.json()["id"], s2.json()["id"]]},
    )
    # Mark S1 completed.
    d1 = r.json()["deliveries"][0]
    await client.patch(f"/api/v1/deliveries/{d1['id']}", json={"status": "completed"})

    urgent = await client.post(
        "/api/v1/stops/",
        json={"name": "U", "address": "U", "lat": 40.5, "lng": -74.0},
    )
    res = await client.post(
        f"/api/v1/routes/{r.json()['id']}/insert-urgent",
        json={"stop_id": urgent.json()["id"]},
    )
    body = res.json()
    # Only S2 was pending; urgent inserted at position 0 (before S2).
    assert body["inserted_at_position"] == 0
    shifted = {s["stop_name"] for s in body["shifted_stops"]}
    assert shifted == {"S2"}
