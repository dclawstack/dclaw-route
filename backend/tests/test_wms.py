import pytest


@pytest.mark.asyncio
async def test_loading_sequence_is_reverse_of_stop_order(client):
    s1 = await client.post(
        "/api/v1/stops/",
        json={"name": "First", "address": "1", "lat": 1.0, "lng": 1.0},
    )
    s2 = await client.post(
        "/api/v1/stops/",
        json={"name": "Second", "address": "2", "lat": 2.0, "lng": 2.0},
    )
    s3 = await client.post(
        "/api/v1/stops/",
        json={"name": "Third", "address": "3", "lat": 3.0, "lng": 3.0},
    )
    r = await client.post(
        "/api/v1/routes/",
        json={"name": "R", "stop_ids": [s1.json()["id"], s2.json()["id"], s3.json()["id"]]},
    )
    route_id = r.json()["id"]

    res = await client.get(f"/api/v1/wms/routes/{route_id}/loading-sequence")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["item_count"] == 3
    # LIFO: Third loads first (load_position 0), First loads last (load_position 2)
    items = body["items"]
    assert items[0]["stop_name"] == "Third"
    assert items[0]["load_position"] == 0
    assert items[0]["delivery_sequence"] == 2
    assert items[2]["stop_name"] == "First"
    assert items[2]["load_position"] == 2
    assert items[2]["delivery_sequence"] == 0


@pytest.mark.asyncio
async def test_loading_sequence_404_missing_route(client):
    r = await client.get(
        "/api/v1/wms/routes/00000000-0000-0000-0000-000000000000/loading-sequence"
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_assign_dock_persists_on_route(client):
    r = await client.post("/api/v1/routes/", json={"name": "R"})
    route_id = r.json()["id"]
    res = await client.post(
        f"/api/v1/wms/routes/{route_id}/dock",
        json={"dock_number": "D-12"},
    )
    assert res.status_code == 200
    assert res.json()["dock_number"] == "D-12"

    route = await client.get(f"/api/v1/routes/{route_id}")
    assert route.json()["dock_number"] == "D-12"


@pytest.mark.asyncio
async def test_loading_manifest_includes_dock(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "A", "lat": 1.0, "lng": 1.0},
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    route_id = r.json()["id"]
    await client.post(f"/api/v1/wms/routes/{route_id}/dock", json={"dock_number": "B-3"})

    manifest = await client.get(f"/api/v1/wms/routes/{route_id}/loading-sequence")
    assert manifest.json()["dock_number"] == "B-3"


@pytest.mark.asyncio
async def test_wms_sync_returns_snapshot_counts(client):
    s = await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "A", "lat": 1.0, "lng": 1.0},
    )
    await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    r = await client.post("/api/v1/wms/sync")
    assert r.status_code == 200
    body = r.json()
    assert body["routes_synced"] == 1
    assert body["deliveries_synced"] == 1
