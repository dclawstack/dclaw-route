import pytest

from app.services.optimizer import haversine_km, _nearest_neighbor, _total_distance


def test_haversine_known_distance():
    nyc = (40.7128, -74.0060)
    la = (34.0522, -118.2437)
    d = haversine_km(*nyc, *la)
    assert 3900 < d < 4000


def test_nearest_neighbor_picks_shorter_path():
    # Four points where the input order is bad and NN is much better.
    pts = [(0, 0), (10, 10), (0, 1), (10, 11)]
    order = _nearest_neighbor(pts, anchor_first=True)
    nn_dist = _total_distance([pts[i] for i in order])
    orig_dist = _total_distance(pts)
    assert nn_dist < orig_dist


@pytest.mark.asyncio
async def test_optimize_route_endpoint(client):
    # Place stops in a deliberately bad order: NYC, LA, Boston, SF.
    # NN from NYC should go NYC -> Boston -> ... (much shorter total).
    coords = [
        ("NYC", 40.7128, -74.0060),
        ("LA", 34.0522, -118.2437),
        ("Boston", 42.3601, -71.0589),
        ("SF", 37.7749, -122.4194),
    ]
    stop_ids = []
    for name, lat, lng in coords:
        r = await client.post(
            "/api/v1/stops/", json={"name": name, "address": name, "lat": lat, "lng": lng}
        )
        stop_ids.append(r.json()["id"])

    r = await client.post(
        "/api/v1/routes/", json={"name": "Tour", "stop_ids": stop_ids}
    )
    route_id = r.json()["id"]

    r2 = await client.post(f"/api/v1/routes/{route_id}/optimize", json={})
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert body["optimized_distance_km"] < body["original_distance_km"]
    assert body["improvement_percent"] > 0
    assert set(body["optimized_sequence"]) == set(body["original_sequence"])

    # Verify the route was persisted with the new total distance.
    r3 = await client.get(f"/api/v1/routes/{route_id}")
    assert r3.json()["total_distance_km"] == body["optimized_distance_km"]


@pytest.mark.asyncio
async def test_optimize_rejects_short_route(client):
    s = await client.post(
        "/api/v1/stops/", json={"name": "X", "address": "X", "lat": 0.0, "lng": 0.0}
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "stop_ids": [s.json()["id"]]}
    )
    route_id = r.json()["id"]
    r2 = await client.post(f"/api/v1/routes/{route_id}/optimize", json={})
    assert r2.status_code == 400


@pytest.mark.asyncio
async def test_optimize_missing_route(client):
    r = await client.post(
        "/api/v1/routes/00000000-0000-0000-0000-000000000000/optimize", json={}
    )
    assert r.status_code == 400
