import pytest


@pytest.mark.asyncio
async def test_create_and_list_territory(client):
    r = await client.post(
        "/api/v1/territories/", json={"name": "North", "color": "#3B82F6"}
    )
    assert r.status_code == 201, r.text
    lst = (await client.get("/api/v1/territories/")).json()
    assert len(lst) == 1
    assert lst[0]["name"] == "North"


@pytest.mark.asyncio
async def test_cluster_assigns_stops_to_n_territories(client):
    # Two tight clusters: NYC-area and SF-area.
    nyc = [(40.71, -74.00), (40.73, -73.99), (40.72, -74.01)]
    sf = [(37.77, -122.42), (37.78, -122.41), (37.76, -122.43)]
    for i, (lat, lng) in enumerate(nyc + sf):
        await client.post(
            "/api/v1/stops/",
            json={"name": f"S{i}", "address": str(i), "lat": lat, "lng": lng},
        )

    r = await client.post("/api/v1/territories/cluster", json={"n": 2})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["assigned_stops"] == 6
    assert len(body["territories"]) == 2
    stop_counts = sorted(t["stop_count"] for t in body["territories"])
    assert stop_counts == [3, 3]

    # Each stop should now have a territory_id.
    stops = (await client.get("/api/v1/stops/")).json()
    assert all(s["territory_id"] is not None for s in stops)


@pytest.mark.asyncio
async def test_cluster_rejects_no_stops(client):
    r = await client.post("/api/v1/territories/cluster", json={"n": 3})
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_cluster_rejects_invalid_n(client):
    await client.post(
        "/api/v1/stops/",
        json={"name": "A", "address": "A", "lat": 1.0, "lng": 1.0},
    )
    r = await client.post("/api/v1/territories/cluster", json={"n": 0})
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_recluster_replaces_previous_territories(client):
    for i in range(4):
        await client.post(
            "/api/v1/stops/",
            json={
                "name": f"S{i}",
                "address": str(i),
                "lat": 40.7 + i * 0.01,
                "lng": -74.0,
            },
        )
    await client.post("/api/v1/territories/cluster", json={"n": 2})
    r = await client.post("/api/v1/territories/cluster", json={"n": 3})
    assert r.status_code == 200
    territories = (await client.get("/api/v1/territories/")).json()
    assert len(territories) == 3
