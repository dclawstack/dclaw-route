import pytest


@pytest.mark.asyncio
async def test_create_and_list_gig_driver(client):
    r = await client.post(
        "/api/v1/gig/drivers",
        json={"name": "Riley", "phone": "+1-555", "rating": 4.8, "vehicle_type": "car"},
    )
    assert r.status_code == 201, r.text
    lst = await client.get("/api/v1/gig/drivers")
    assert len(lst.json()) == 1


@pytest.mark.asyncio
async def test_request_picks_highest_rated_when_no_geo(client):
    await client.post(
        "/api/v1/gig/drivers",
        json={"name": "Low", "rating": 3.5, "vehicle_type": "car"},
    )
    await client.post(
        "/api/v1/gig/drivers",
        json={"name": "High", "rating": 4.9, "vehicle_type": "car"},
    )
    route = await client.post("/api/v1/routes/", json={"name": "Overflow"})

    res = await client.post(
        "/api/v1/gig/request",
        json={"route_id": route.json()["id"]},
    )
    assert res.status_code == 200, res.text
    assert res.json()["gig_driver_name"] == "High"


@pytest.mark.asyncio
async def test_request_picks_nearest_when_geo_provided(client):
    await client.post(
        "/api/v1/gig/drivers",
        json={
            "name": "Far",
            "rating": 5.0,
            "vehicle_type": "car",
            "current_lat": 50.0,
            "current_lng": -110.0,
        },
    )
    await client.post(
        "/api/v1/gig/drivers",
        json={
            "name": "Near",
            "rating": 4.5,
            "vehicle_type": "car",
            "current_lat": 40.71,
            "current_lng": -74.0,
        },
    )
    route = await client.post("/api/v1/routes/", json={"name": "Local"})

    res = await client.post(
        "/api/v1/gig/request",
        json={
            "route_id": route.json()["id"],
            "near_lat": 40.7128,
            "near_lng": -74.0060,
        },
    )
    body = res.json()
    assert body["gig_driver_name"] == "Near"
    assert body["distance_km"] is not None
    assert body["distance_km"] < 10


@pytest.mark.asyncio
async def test_request_filters_by_vehicle_type(client):
    await client.post(
        "/api/v1/gig/drivers",
        json={"name": "BikeOnly", "rating": 5.0, "vehicle_type": "bike"},
    )
    route = await client.post("/api/v1/routes/", json={"name": "R"})
    res = await client.post(
        "/api/v1/gig/request",
        json={"route_id": route.json()["id"], "vehicle_type": "car"},
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_request_marks_chosen_busy_and_release_frees(client):
    g = await client.post(
        "/api/v1/gig/drivers",
        json={"name": "Solo", "rating": 4.5, "vehicle_type": "car"},
    )
    route = await client.post("/api/v1/routes/", json={"name": "R"})
    await client.post(
        "/api/v1/gig/request", json={"route_id": route.json()["id"]}
    )

    drivers = (await client.get("/api/v1/gig/drivers")).json()
    assert drivers[0]["status"] == "busy"
    assert drivers[0]["current_route_id"] == route.json()["id"]

    # A second request should fail — nobody left.
    route2 = await client.post("/api/v1/routes/", json={"name": "R2"})
    second = await client.post(
        "/api/v1/gig/request", json={"route_id": route2.json()["id"]}
    )
    assert second.status_code == 400

    # Release frees them up.
    released = await client.post(f"/api/v1/gig/release/{g.json()['id']}")
    assert released.json()["status"] == "available"
    assert released.json()["current_route_id"] is None


@pytest.mark.asyncio
async def test_request_respects_min_rating(client):
    await client.post(
        "/api/v1/gig/drivers",
        json={"name": "Mid", "rating": 3.2, "vehicle_type": "car"},
    )
    route = await client.post("/api/v1/routes/", json={"name": "R"})
    res = await client.post(
        "/api/v1/gig/request",
        json={"route_id": route.json()["id"], "min_rating": 4.0},
    )
    assert res.status_code == 400
