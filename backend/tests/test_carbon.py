import pytest


@pytest.mark.asyncio
async def test_route_emissions_zero_without_vehicle(client):
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "total_distance_km": 100.0}
    )
    res = await client.get(f"/api/v1/carbon/routes/{r.json()['id']}/emissions")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["co2_total_kg"] == 0
    assert body["vehicle_id"] is None


@pytest.mark.asyncio
async def test_route_emissions_calculation(client):
    v = await client.post(
        "/api/v1/vehicles/",
        json={"plate": "VAN-1", "co2_g_per_km": 250.0, "capacity_kg": 1000},
    )
    r = await client.post(
        "/api/v1/routes/",
        json={
            "name": "R",
            "total_distance_km": 100.0,
            "vehicle_id": v.json()["id"],
        },
    )
    res = await client.get(f"/api/v1/carbon/routes/{r.json()['id']}/emissions")
    # 100 km * 250 g/km / 1000 = 25 kg
    assert res.json()["co2_total_kg"] == 25.0
    assert res.json()["vehicle_plate"] == "VAN-1"


@pytest.mark.asyncio
async def test_optimize_vehicle_picks_lowest_co2(client):
    await client.post(
        "/api/v1/vehicles/",
        json={"plate": "DIESEL", "co2_g_per_km": 900.0, "capacity_kg": 2000},
    )
    await client.post(
        "/api/v1/vehicles/",
        json={"plate": "EV", "co2_g_per_km": 50.0, "capacity_kg": 1000},
    )
    r = await client.post(
        "/api/v1/routes/", json={"name": "R", "total_distance_km": 100.0}
    )
    res = await client.post(
        f"/api/v1/carbon/routes/{r.json()['id']}/optimize-vehicle"
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["chosen_plate"] == "EV"
    # Savings vs DIESEL: 100 km * (900 - 50) / 1000 = 85 kg
    assert body["co2_saved_kg"] == 85.0

    # Route now has EV assigned.
    route = await client.get(f"/api/v1/routes/{r.json()['id']}")
    assert route.json()["vehicle_id"] == res.json()["chosen_vehicle_id"]


@pytest.mark.asyncio
async def test_optimize_rejects_no_available_vehicle(client):
    r = await client.post("/api/v1/routes/", json={"name": "R"})
    res = await client.post(
        f"/api/v1/carbon/routes/{r.json()['id']}/optimize-vehicle"
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_fleet_emissions_aggregates(client):
    v = await client.post(
        "/api/v1/vehicles/",
        json={"plate": "V1", "co2_g_per_km": 200.0},
    )
    await client.post(
        "/api/v1/routes/",
        json={
            "name": "R1",
            "total_distance_km": 50.0,
            "vehicle_id": v.json()["id"],
        },
    )
    await client.post(
        "/api/v1/routes/",
        json={
            "name": "R2",
            "total_distance_km": 50.0,
            "vehicle_id": v.json()["id"],
        },
    )
    res = await client.get("/api/v1/carbon/summary")
    body = res.json()
    # 2 routes * 50 km * 200 g/km / 1000 = 20 kg total
    assert body["total_co2_kg"] == 20.0
    assert body["total_distance_km"] == 100.0
    assert body["avg_co2_g_per_km"] == 200.0
    assert body["route_count"] == 2


@pytest.mark.asyncio
async def test_emissions_404(client):
    r = await client.get(
        "/api/v1/carbon/routes/00000000-0000-0000-0000-000000000000/emissions"
    )
    assert r.status_code == 404
